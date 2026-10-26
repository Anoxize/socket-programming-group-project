"""Discovery qua UDP broadcast: một socket dùng chung, thread Broadcaster và Listener.

Mục đích: tạo một socket UDP dùng cho cả gửi lẫn nhận. Thread broadcaster gửi
HELLO mỗi ``BROADCAST_INTERVAL`` (3 s) và gửi ngay khi ``/status`` đổi. Thread listener
nhận gói, cập nhật ``PeerRegistry`` và quét timeout mỗi ``SWEEP_INTERVAL`` (1 s).
Nền tảng: ``udp_broadcast_demo.py`` của giảng viên (``make_socket``, vòng gửi 3 s).
Owner: Thành viên B.
Phục vụ yêu cầu: B1, B2, B3, B4, C1, C2, F6, H2, H3, N3, N4; rubric: M1.
Được import (Phần 3.1): ``config``, ``protocol``, ``peer_registry``.
Không import ``chat_manager``/``ui``: Listener báo sự kiện qua callback ``on_event``.
Luồng chạy code ở đây (Phần 3.2):
- ``udp-broadcaster``: ``Broadcaster.run`` (block ở ``_wake.wait``).
- ``udp-listener``: ``Listener.run`` (block ở ``recvfrom`` với timeout 1 s).
- ``MainThread``: ``set_status``/``announce_now`` (``/status``), ``send_bye`` (``/quit``), ``make_udp_socket``.
Khóa: ``Broadcaster._lock`` bảo vệ ``_status``. Listener gọi registry (khóa riêng của nó),
rồi mới gọi ``on_event`` SAU KHI khóa registry đã nhả (quy tắc khóa 2).
"""

from __future__ import annotations

import socket
import threading
from typing import Callable

from lanchat.config import (  # noqa: F401  (dùng khi viết thân hàm)
    BROADCAST_INTERVAL,
    MAX_DATAGRAM,
    STATUSES,
    SWEEP_INTERVAL,
    Identity,
)
from lanchat.peer_registry import PeerEvent, PeerRegistry
from lanchat.protocol import encode_hello, encode_udp_bye, parse_datagram  # noqa: F401


def make_udp_socket(port: int) -> socket.socket:
    """UDP socket with SO_REUSEADDR (+SO_REUSEPORT if present), SO_BROADCAST, bound to ('', port), timeout 1 s.

    Gợi ý:
    - Xem lại ``make_socket()`` trong ``udp_broadcast_demo.py`` của thầy: thứ tự đặt option rất quan trọng, mọi ``setsockopt`` phải đứng TRƯỚC ``bind``.
    - ``SO_REUSEPORT`` không có trên Windows và có thể lỗi trên vài hệ: kiểm có tồn tại không và bắt lỗi (D21).
    - Bind ``""`` nghĩa là mọi interface. Không bind ``127.0.0.1`` (sẽ không nhận được gói từ máy khác).
    - Đặt timeout 1 s để ``Listener`` thoát được khi ``stop_event`` bật (D24).
    - Vấn đáp câu 2 (Phần 9.1) hỏi đúng hàm này.
    """
    raise NotImplementedError("TODO(B): make_udp_socket")


def guess_local_ip() -> str:
    """Best-effort LAN IP via a connected UDP socket (no packet sent); '127.0.0.1' on failure.

    Gợi ý:
    - "Connect" một socket UDP tới một địa chỉ ngoài chỉ để hệ điều hành chọn interface ra; UDP connect không gửi gói nào.
    - Mọi lỗi đều trả ``'127.0.0.1'``, không ném lỗi.
    - Chỉ dùng để in thông tin (banner). IP thật của peer lấy từ ``addr[0]`` của ``recvfrom``.
    - Đóng socket tạm sau khi dùng.
    """
    raise NotImplementedError("TODO(B): guess_local_ip")


class Broadcaster(threading.Thread):
    """Periodic HELLO sender (thread name 'udp-broadcaster')."""

    # nội bộ: _lock, _status, _wake: threading.Event, _send_hello()

    def __init__(self, sock: socket.socket, ident: Identity, bcast: str, udp_port: int,
                 stop_event: threading.Event) -> None:
        """Prepare periodic HELLO sender with initial status 'online'.

        Gợi ý:
        - Gọi ``super().__init__`` với ``name="udp-broadcaster"`` và ``daemon=True`` (daemon chỉ là lưới an toàn cuối, Phần 3.4).
        - Tạo ``_lock``, ``_status = "online"`` và ``_wake = threading.Event()``.
        - Không gửi gì trong ``__init__``. Thread chưa chạy.
        """
        raise NotImplementedError("TODO(B): Broadcaster.__init__")

    def run(self) -> None:
        """Loop: send HELLO, then wait on _wake up to BROADCAST_INTERVAL; exit when stop_event set.

        Gợi ý:
        - Dùng ``_wake.wait(timeout)`` thay cho ``time.sleep``: ``/status`` và shutdown đánh thức được ngay (D17).
        - Nhớ xóa cờ ``_wake`` sau khi thức dậy, nếu không vòng lặp sẽ quay liên tục.
        - Lỗi gửi (vd. mạng rớt) không được giết thread: bắt ``OSError``, ghi log, vòng sau thử lại.
        - Bọc cả thân bằng ``try/except Exception`` và ``notify``/log lỗi nội bộ (quy tắc khóa 5).
        - Test: T-I08, T-N01 (thấy HELLO mỗi 3 s bằng ``nc -ul 9999``).
        """
        raise NotImplementedError("TODO(B): Broadcaster.run")

    def _send_hello(self) -> None:
        """Send one HELLO with the current status to (bcast, udp_port).

        Gợi ý:
        - Đọc ``_status`` dưới ``_lock``, nhả khóa rồi mới ``sendto`` (quy tắc khóa 1: không I/O mạng khi giữ khóa dữ liệu).
        - Payload tạo bằng ``protocol.encode_hello``.
        """
        raise NotImplementedError("TODO(B): Broadcaster._send_hello")

    @property
    def status(self) -> str:
        """Current own status.

        Gợi ý:
        - Đọc dưới ``_lock``. Toolbar gọi hàm này mỗi 0.5 s.
        """
        raise NotImplementedError("TODO(B): Broadcaster.status")

    def set_status(self, status: str) -> None:
        """Validate and change own status, then announce_now(); raise ValueError if invalid.

        Gợi ý:
        - Chỉ chấp nhận giá trị trong ``STATUSES``. ``/status busy`` phải báo usage (T-U39).
        - Ghi dưới khóa, nhả khóa rồi gọi ``announce_now()``.
        - Test: T-M04 (bên kia thấy ``is now away`` trong ≤ 1 s).
        """
        raise NotImplementedError("TODO(B): Broadcaster.set_status")

    def announce_now(self) -> None:
        """Wake the loop to broadcast immediately.

        Gợi ý:
        - Chỉ cần bật ``_wake``. Shutdown cũng gọi hàm này để thread thoát nhanh (Phần 3.4 bước 4).
        """
        raise NotImplementedError("TODO(B): Broadcaster.announce_now")

    def send_bye(self) -> None:
        """Send one UDP BYE datagram (called once on /quit).

        Gợi ý:
        - Gửi trực tiếp từ thread gọi (``MainThread`` trong ``App.shutdown``), không đợi vòng lặp.
        - Lỗi gửi chỉ ghi log, không làm hỏng quá trình tắt.
        - Test: T-U21 (phía nhận), T-M03, ảnh Wireshark W6.
        """
        raise NotImplementedError("TODO(B): Broadcaster.send_bye")


class Listener(threading.Thread):
    """UDP receiver feeding the registry (thread name 'udp-listener')."""

    def __init__(self, sock: socket.socket, registry: PeerRegistry,
                 on_event: Callable[[PeerEvent], None], stop_event: threading.Event) -> None:
        """Prepare receiver that feeds the registry and reports PeerEvents.

        Gợi ý:
        - ``name="udp-listener"``, ``daemon=True``.
        - ``on_event`` được ``App`` nối vào ``ChatManager.on_peer_event``. Listener không biết gì về ChatManager.
        """
        raise NotImplementedError("TODO(B): Listener.__init__")

    def run(self) -> None:
        """Loop: recvfrom (1 s timeout) -> parse_datagram -> registry.handle_datagram; expire() every SWEEP_INTERVAL.

        Gợi ý:
        - ``socket.timeout`` không phải lỗi: đó là lúc kiểm ``stop_event`` và quét ``expire()``.
        - Gói nhiều nhưng không bao giờ timeout thì sao? Phải quét theo thời gian đã trôi qua, không chỉ khi timeout xảy ra.
        - ``parse_datagram`` trả ``None`` thì bỏ qua lặng lẽ (T-N02: gói rác không làm app lỗi).
        - Gọi ``on_event`` cho từng sự kiện sau khi registry đã trả về (khóa registry đã nhả).
        - Socket bị đóng khi shutdown sẽ làm ``recvfrom`` ném ``OSError``: nếu ``stop_event`` đã bật thì thoát êm.
        """
        raise NotImplementedError("TODO(B): Listener.run")
