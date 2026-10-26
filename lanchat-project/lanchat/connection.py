"""Lõi TCP P2P: socket listen, acceptor, dial, handshake INTR, tie-break, recv loop.

Mục đích: mỗi peer vừa là server (listen + accept) vừa là client (connect). Mỗi kết nối
chat có một thread nhận riêng. Gửi frame luôn dưới ``Connection.send_lock``. Kết nối nào
có frame đầu là ``FILE`` thì chuyển cho callback ``on_file_socket``, nhờ vậy file này
KHÔNG import ``file_transfer``.
Owner: Thành viên A.
Phục vụ yêu cầu: A5, D1, D5, H4, H5, H7, I2, I3, J1, J2; rubric: M2, M5, M6.
Được import (Phần 3.1, quy tắc 2): ``config``, ``protocol``. KHÔNG import
``file_transfer``, ``chat_manager``, ``ui``. Mọi thứ phía trên được gọi qua callback.
Luồng chạy code ở đây (Phần 3.2):
- ``MainThread``: ``connect`` (``/chat``, block tối đa ``CONNECT_TIMEOUT``), ``disconnect`` (``/leave``), ``Connection.send*``.
- ``tcp-acceptor``: ``_accept_loop`` (block ở ``accept()`` với timeout 1 s).
- ``tcp-in-<ip>:<port>``: ``_handle_incoming`` (chờ frame đầu, timeout ``HANDSHAKE_TIMEOUT``).
- ``recv-<name>``: ``_recv_loop`` (``recv_frame`` blocking, không timeout, D26).
- ``MainThread`` lúc shutdown: ``close_all``.
Khóa: ``ConnectionManager._lock`` bảo vệ ``_conns``; mỗi ``Connection`` có ``send_lock``
riêng (ngoại lệ hợp lệ của quy tắc 1 vì nó tồn tại để bọc I/O). Callback ``on_frame``/
``on_closed`` luôn gọi SAU KHI đã nhả ``_lock``.
"""

from __future__ import annotations

import socket
import threading
from typing import Callable

from lanchat.config import (  # noqa: F401  (dùng khi viết thân hàm)
    CONNECT_TIMEOUT,
    HANDSHAKE_TIMEOUT,
    Identity,
)
from lanchat.protocol import (  # noqa: F401  (dùng khi viết thân hàm)
    T_BYE,
    T_ERR,
    T_FILE,
    T_INTRO,
    T_MSG,
    BadFrame,
    Frame,
    FrameError,
    PeerClosed,
    TruncatedFrame,
    decode_json,
    make_bye,
    make_err,
    make_intro,
    make_msg,
    recv_frame,
    send_frame,
)


class ConnectError(Exception):
    """Dial or INTR handshake failed (refused, timeout, wrong peer, protocol error)."""


class Connection:
    """One established, introduced chat connection to a peer."""

    # thuộc tính: peer_id, name, ip, tcp_port, outbound, send_lock, closed

    def __init__(self, sock: socket.socket, peer_id: str, name: str, ip: str,
                 tcp_port: int, outbound: bool) -> None:
        """Wrap an established, introduced chat socket; creates send_lock.

        Gợi ý:
        - Lưu đủ các thuộc tính trong comment ở trên. ``tcp_port`` là LISTEN port của peer (lấy từ INTR), không phải port nguồn ephemeral.
        - ``outbound=True`` khi mình là bên dial. Thông tin này cần cho tie-break D03.
        - Tạo ``send_lock`` riêng cho socket này và cờ ``closed``.
        - Socket chat không đặt timeout đọc (D26). Hãy chắc chắn timeout của bước handshake đã được gỡ trước khi bọc vào đây.
        """
        raise NotImplementedError("TODO(A): Connection.__init__")

    def send(self, ftype: bytes, payload: bytes) -> None:
        """Send one whole frame under send_lock; raise ConnectionError if closed or send fails.

        Gợi ý:
        - Mỗi lần giữ ``send_lock`` gửi trọn đúng một frame (quy tắc khóa 3).
        - Đổi lỗi socket (``OSError``) thành ``ConnectionError`` để ``ChatManager`` chỉ cần bắt một loại.
        - Kết nối đã đóng thì báo lỗi ngay, không cố gửi.
        """
        raise NotImplementedError("TODO(A): Connection.send — gửi dưới send_lock")

    def send_msg(self, text: str) -> None:
        """Encode and send a MSG frame.

        Gợi ý:
        - Dùng ``make_msg`` (nó tự chặn chuỗi rỗng và quá dài) rồi ``send``.
        """
        raise NotImplementedError("TODO(A): Connection.send_msg")

    def initiator_id(self, my_peer_id: str) -> str:
        """peer_id of whoever opened this TCP connection (for tie-break).

        Gợi ý:
        - Outbound thì người khởi tạo là mình, ngược lại là peer.
        - D03: giữ kết nối do peer có peer_id nhỏ hơn khởi tạo. Hai bên phải tự tính ra cùng một kết quả.
        """
        raise NotImplementedError("TODO(A): Connection.initiator_id")

    def close(self, reason: str = "leave", send_bye: bool = True) -> None:
        """Idempotent: optionally send BYE, then shutdown(SHUT_RDWR) and close the socket.

        Gợi ý:
        - Gọi nhiều lần không được lỗi (idempotent). Đặt cờ ``closed`` trước để các lần sau bỏ qua.
        - Gửi BYE là "cố gắng": socket có thể đã chết, lỗi khi gửi BYE thì bỏ qua.
        - ``shutdown`` trước ``close`` để thread ``recv-*`` đang block được đánh thức (``recv`` trả ``b''``).
        - Wireshark W4: ``/leave`` phải thấy FIN, không phải RST.
        """
        raise NotImplementedError("TODO(A): Connection.close")


class ConnectionManager:
    """Owns the listening socket and all chat connections (keyed by peer_id)."""

    # nội bộ:
    # _accept_loop()                         thread 'tcp-acceptor'
    # _handle_incoming(sock, addr)           thread 'tcp-in-<ip>:<port>': chờ frame đầu INTR/FILE
    # _register(conn) -> Connection          check-and-insert + tie-break dưới _lock
    # _start_receiver(conn)                  thread 'recv-<name>'
    # _recv_loop(conn)                       recv_frame lặp; BYE/EOF/lỗi -> _unregister + on_closed
    # _unregister(conn, reason)

    def __init__(self, ident: Identity, stop_event: threading.Event,
                 on_frame: Callable[[Connection, Frame], None],
                 on_closed: Callable[[Connection, str], None],
                 on_file_socket: Callable[[socket.socket, tuple[str, int], dict], None]) -> None:
        """Store callbacks; no sockets opened yet.

        Gợi ý:
        - Lưu identity, ``stop_event``, ba callback; tạo ``_conns: dict[str, Connection]`` và ``_lock``.
        - Chưa mở socket ở đây để test có thể tạo đối tượng mà không chiếm port.
        - Test loopback dùng port 0. Hãy nghĩ cách cho test biết port thật sau khi ``start()`` (vd. lưu lại port đã bind).
        """
        raise NotImplementedError("TODO(A): ConnectionManager.__init__")

    def start(self) -> None:
        """Bind ('', tcp_port), listen(8), start 'tcp-acceptor'; raise OSError if port busy.

        Gợi ý:
        - Port bận thì để ``OSError`` nổi lên. ``App.run`` sẽ in lỗi rõ ràng và thoát mã 2 (D21, T-M01). Không tự tăng port.
        - KHÔNG bật ``SO_REUSEADDR`` cho socket TCP listen trên Windows (lỗi "hijack port", D21).
        - Đặt timeout 1 s cho socket listen để ``_accept_loop`` kiểm được ``stop_event`` (D24).
        - Vấn đáp câu 17: ``listen(8)`` nghĩa là gì?
        """
        raise NotImplementedError("TODO(A): ConnectionManager.start")

    def connect(self, peer_id: str, ip: str, tcp_port: int) -> Connection:
        """Return existing connection or dial (CONNECT_TIMEOUT), exchange INTR, register, start receiver.

        Gợi ý:
        - Đã có kết nối sống tới peer_id thì trả luôn, không dial lại (sequence 2: "kết nối có sẵn").
        - Thứ tự: dial có timeout → gửi INTR của mình → chờ INTR trả lời (cũng có timeout) → kiểm peer_id đúng người định gọi (D04) → ``_register`` → ``_start_receiver``.
        - Mọi thất bại (refused, timeout, sai peer, frame lạ) đổi thành ``ConnectError`` với lý do ngắn; nhớ đóng socket dở dang (T-I04, T-I10, T-N04).
        - Không giữ ``_lock`` trong lúc dial hay chờ INTR (quy tắc khóa 1).
        - Chạy trên ``MainThread`` nên tổng thời gian phải ≤ khoảng 3.5 s để UI không treo lâu.
        """
        raise NotImplementedError("TODO(A): ConnectionManager.connect — dial + INTR")

    def get(self, peer_id: str) -> Connection | None:
        """Live connection to peer_id, if any.

        Gợi ý:
        - Đọc dưới ``_lock``. Kết nối đã ``closed`` thì coi như không có.
        """
        raise NotImplementedError("TODO(A): ConnectionManager.get")

    def active(self) -> list[Connection]:
        """Snapshot of live connections.

        Gợi ý:
        - Trả list mới (copy) để bên gọi duyệt mà không cần giữ khóa.
        """
        raise NotImplementedError("TODO(A): ConnectionManager.active")

    def disconnect(self, peer_id: str, reason: str = "leave") -> bool:
        """Close the connection to peer_id with BYE; False if none.

        Gợi ý:
        - Lấy kết nối ra khỏi bảng dưới khóa, nhả khóa rồi mới ``close`` (gửi BYE là I/O mạng).
        - Thread ``recv-*`` của kết nối đó sẽ tự thoát khi socket đóng. Cẩn thận đừng báo ``on_closed`` hai lần cho cùng một lần đóng chủ động.
        - Test: T-M08, Wireshark W4 (FIN).
        """
        raise NotImplementedError("TODO(A): ConnectionManager.disconnect")

    def close_all(self, reason: str = "quit") -> None:
        """Send BYE on and close every connection; close the listening socket.

        Gợi ý:
        - Gọi trong ``App.shutdown`` bước 2 (Phần 3.4).
        - Copy danh sách kết nối dưới khóa, nhả khóa, rồi đóng từng cái.
        - Một kết nối lỗi khi đóng không được chặn việc đóng các kết nối còn lại.
        - Test: T-I09, T-M14.
        """
        raise NotImplementedError("TODO(A): ConnectionManager.close_all")

    # ------------------------------------------------------------------ nội bộ
    def _accept_loop(self) -> None:
        """Thread 'tcp-acceptor': accept() with 1 s timeout, spawn one 'tcp-in-<ip>:<port>' thread per socket.

        Gợi ý:
        - Không làm handshake ở đây. Acceptor chỉ ``accept`` rồi giao cho thread mới, để một peer chậm không chặn peer khác (T-I06).
        - ``socket.timeout`` là lúc kiểm ``stop_event``.
        - Socket listen bị đóng khi shutdown sẽ làm ``accept`` ném ``OSError``: thoát êm nếu đang dừng.
        - Bọc thân bằng ``try/except Exception`` (quy tắc khóa 5). Acceptor chết là không ai kết nối được nữa.
        """
        raise NotImplementedError("TODO(A): _accept_loop")

    def _handle_incoming(self, sock: socket.socket, addr: tuple[str, int]) -> None:
        """Thread 'tcp-in-<ip>:<port>': wait for the first frame (INTR or FILE) and route the socket.

        Gợi ý:
        - Chờ frame đầu với ``HANDSHAKE_TIMEOUT``. Quá hạn hoặc frame rác → (nếu được) gửi ``ERR not_intro``/``bad_frame``, đóng socket (T-I06, T-N03).
        - Frame đầu là ``FILE``: decode meta, rồi giao ``(sock, addr, meta)`` cho ``on_file_socket``. Từ đây socket thuộc về TransferManager.
        - Frame đầu là ``INTR``: trả INTR của mình, tạo ``Connection`` (outbound=False), ``_register``, rồi đổi tên thread thành ``recv-<name>`` và chạy ``_recv_loop`` ngay trên thread này.
        - Nhận diện người gọi bằng INTR, không bằng port nguồn (port nguồn là ephemeral, D04).
        - In ``[!] Protocol error from <ip>: bad frame — connection closed`` thì cần ``notify``; ConnectionManager không có notify, hãy nghĩ cách báo qua callback hoặc log.
        """
        raise NotImplementedError("TODO(A): _handle_incoming — INTR/FILE")

    def _register(self, conn: Connection) -> Connection:
        """Check-and-insert under _lock with the D03 tie-break; return the connection that is kept.

        Gợi ý:
        - Kiểm tra và chèn phải nằm trong CÙNG một lần giữ ``_lock``, nếu không hai thread có thể cùng chèn (race).
        - Đã có kết nối tới peer_id đó: giữ kết nối do peer có peer_id nhỏ hơn khởi tạo (``initiator_id``), kết nối kia đóng bằng ``BYE duplicate``.
        - Việc đóng kết nối bị loại (I/O) làm SAU khi nhả khóa.
        - Test: T-I03 (hai bên ``connect`` cùng lúc bằng ``threading.Barrier``).
        """
        raise NotImplementedError("TODO(A): _register — tie-break D03")

    def _start_receiver(self, conn: Connection) -> None:
        """Start thread 'recv-<name>' running _recv_loop(conn) (used after an outbound dial).

        Gợi ý:
        - Đặt tên thread đúng quy ước để ``/threads`` hiện ``recv-Minh`` (T-M19).
        - ``daemon=True`` chỉ là lưới an toàn; shutdown vẫn phải đóng socket để thread thoát.
        """
        raise NotImplementedError("TODO(A): _start_receiver")

    def _recv_loop(self, conn: Connection) -> None:
        """Loop recv_frame; MSG -> on_frame; BYE/EOF/error -> _unregister + on_closed.

        Gợi ý:
        - Chỉ chấp nhận ``MSG ``, ``BYE ``, ``ERR `` sau khi đã ESTABLISHED (máy trạng thái 4.3).
        - Ánh xạ kết cục ra ``reason`` cho ``on_closed``: BYE thì lấy lý do trong payload; ``PeerClosed`` không kèm BYE hay ``TruncatedFrame`` hay ``ConnectionResetError`` thì ``"lost"`` (T-I05); ``BadFrame`` thì gửi ``ERR bad_frame`` rồi đóng.
        - Lần đóng do chính mình chủ động (``disconnect``/``close_all``) cũng làm ``recv`` trả lỗi: phân biệt để không in "connection lost" sai.
        - Callback ``on_frame`` chạy trên thread này, nên ChatManager phải xử lý nhanh và không gọi ``prompt()``.
        - Phần 9.2 #5: thêm loại frame mới (``TYPN``…) thì sửa nhánh xử lý ở đây.
        """
        raise NotImplementedError("TODO(A): _recv_loop")

    def _unregister(self, conn: Connection, reason: str) -> None:
        """Remove conn from _conns (only if it is still the registered one) and close it.

        Gợi ý:
        - Chỉ xóa nếu entry trong bảng đúng là ``conn`` này: sau tie-break, peer_id đó có thể đã trỏ tới kết nối khác.
        - Xóa dưới khóa, đóng socket sau khi nhả khóa.
        """
        raise NotImplementedError("TODO(A): _unregister")
