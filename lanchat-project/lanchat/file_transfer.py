"""Truyền file: kết nối TCP riêng cho mỗi file, ``.part`` → SHA-256 → ``os.replace``.

Mục đích: gửi file trên thread riêng qua kết nối TCP riêng (D12) để chat không bị
chặn (E4). Nhận file vào ``downloads/`` theo cơ chế ghi ``.part``, kiểm SHA-256 rồi mới
đổi tên (D14). Báo tiến độ 25/50/75/100% (D13). Hai hàm stream tách ra mức module để
test bằng ``socketpair``.
Owner: Thành viên C.
Phục vụ yêu cầu: E1, E2, E3, E4, H6, J3, J4; rubric: M3, M6.
Được import (Phần 3.1): ``config``, ``protocol`` (cộng ``hashlib``, ``os``, ``pathlib``).
Không import ``connection``, ``chat_manager``, ``ui``, ``commands``. Kết nối file đến được
``ConnectionManager`` chuyển sang qua callback ``on_file_socket`` (nối vào ``handle_incoming``).
Luồng chạy code ở đây (Phần 3.2):
- ``MainThread``: ``send_file`` (kiểm tra đầu vào), ``active``, ``cancel_all``.
- ``file-send-<tid>``: ``_send_worker``.
- ``file-recv-<tid>`` (đổi tên từ ``tcp-in-*``): ``handle_incoming``.
Khóa: ``TransferManager._lock`` bảo vệ ``_active``, ``_socks``, ``_next_tid``. Không đọc/ghi
file hay socket khi đang giữ khóa này. ``notify`` (``Console._print_lock``) gọi sau khi nhả khóa.
"""

from __future__ import annotations

import hashlib  # noqa: F401  (dùng khi viết stream)
import os  # noqa: F401  (os.replace, os.remove)
import socket
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Callable

from lanchat.config import (  # noqa: F401  (dùng khi viết thân hàm)
    CONNECT_TIMEOUT,
    FILE_CHUNK,
    FILE_IO_TIMEOUT,
    MAX_FILE_SIZE,
    Identity,
)
from lanchat.protocol import (  # noqa: F401  (dùng khi viết thân hàm)
    T_ACK,
    T_ERR,
    T_FILE,
    BadFrame,
    FrameError,
    TruncatedFrame,
    decode_json,
    make_ack,
    make_err,
    make_file_meta,
    recv_frame,
    send_frame,
)


class TransferError(Exception):
    """Transfer failed (peer closed, timeout, ERR from peer, checksum mismatch, I/O error)."""


def safe_filename(name: str) -> str:
    """Strip directories (both / and \\), replace forbidden chars, avoid Windows reserved names, cap 255 bytes; never empty.

    Gợi ý:
    - Tên đến từ mạng là dữ liệu không tin cậy: chống path traversal kiểu ``../../x`` và ``..\\..\\x`` (D15). Phải bỏ thư mục theo CẢ HAI loại dấu gạch, bất kể đang chạy trên OS nào.
    - Thay các ký tự Windows cấm (``<>:"/\\|?*`` và ký tự điều khiển). Chặn tên dành riêng (``CON``, ``NUL``, ``COM1``…, kể cả khi có đuôi).
    - Giới hạn 255 BYTE UTF-8, không phải 255 ký tự. Cắt sao cho không làm gãy giữa một ký tự nhiều byte và cố giữ lại đuôi file.
    - Kết quả không bao giờ rỗng và không phải ``.``/``..``. Tên tiếng Việt như ``báo cáo.pdf`` giữ nguyên.
    - Test: T-U30 (parametrize), vấn đáp câu 13.
    """
    raise NotImplementedError("TODO(C): safe_filename — chống path traversal")


def unique_path(folder: Path, name: str) -> Path:
    """Return folder/name or 'name (1).ext', 'name (2).ext'… not clashing with existing file or .part.

    Gợi ý:
    - Trùng với file đã có HOẶC với một file ``.part`` đang nhận dở đều tính là trùng (T-U31).
    - Tách phần tên và đuôi để số nằm trước đuôi: ``báo cáo (1).pdf`` (T-M15).
    - Hàm này chỉ chọn tên; việc "giữ chỗ" an toàn khi hai file cùng tên đến đồng thời là nhờ mở ``.part`` bằng chế độ ``'xb'``.
    """
    raise NotImplementedError("TODO(C): unique_path")


def human_size(n: int) -> str:
    """Format bytes as '512 B', '2.4 MB', '1.1 GB'.

    Gợi ý:
    - Dùng bậc 1024 và một chữ số thập phân cho KB/MB/GB; byte thì không có phần thập phân.
    - Ví dụ chuẩn: 2 516 582 byte → ``2.4 MB`` (sequence 3).
    """
    raise NotImplementedError("TODO(C): human_size")


def send_stream(sock: socket.socket, f: BinaryIO, size: int,
                on_progress: Callable[[int], None]) -> str:
    """Send exactly size raw bytes in FILE_CHUNK pieces; return SHA-256 hex.

    Gợi ý:
    - Đọc từng khối ``FILE_CHUNK`` và gửi bằng ``sendall``. Cập nhật SHA-256 song song trong lúc gửi, không đọc file hai lần.
    - Gửi đúng ``size`` byte: file bị cắt ngắn giữa chừng (đọc ra ít hơn) là lỗi, phải báo ``TransferError``.
    - Gọi ``on_progress(tổng_đã_gửi)`` sau mỗi khối; tổng cuối cùng phải bằng ``size`` (T-U32).
    - Không có header frame trong phần dữ liệu thô (máy trạng thái file, Phần 4.3).
    """
    raise NotImplementedError("TODO(C): send_stream")


def recv_stream(sock: socket.socket, f: BinaryIO, size: int,
                on_progress: Callable[[int], None]) -> str:
    """Receive exactly size raw bytes into f; raise TruncatedFrame on early EOF; return SHA-256 hex.

    Gợi ý:
    - Không bao giờ xin nhiều hơn số byte còn thiếu, nếu không sẽ "ăn" luôn frame ``ACK sent`` phía sau.
    - ``recv`` trả ``b''`` trước khi đủ ``size`` → ``TruncatedFrame`` (J4, T-U33).
    - Ghi vào ``f`` và cập nhật SHA-256 cho từng mảnh nhận được.
    - Socket file có timeout ``FILE_IO_TIMEOUT``: để ``socket.timeout`` nổi lên cho bên gọi xử lý.
    """
    raise NotImplementedError("TODO(C): recv_stream")


class ProgressReporter:
    """Prints '... 25%' style lines only when a step boundary is crossed."""

    def __init__(self, label: str, size: int, notify: Callable[[str], None], step: int = 25) -> None:
        """Print progress lines only when percent crosses a multiple of step.

        Gợi ý:
        - Lưu nhãn (vd. ``Sending slides.pdf``), kích thước, ``notify``, bước và mốc đã in gần nhất.
        - Phần 9.2 #4: đổi bước 25 → 10 chỉ bằng tham số ``step``.
        """
        raise NotImplementedError("TODO(C): ProgressReporter.__init__")

    def update(self, done: int) -> None:
        """Record bytes done; maybe print '... 50%'.

        Gợi ý:
        - Gọi 1000 lần cũng chỉ in đúng 4 dòng 25/50/75/100 (T-U35). Một lần nhảy qua nhiều mốc thì in mốc nào?
        - Dùng phép chia số nguyên, tránh sai số float khi so mốc.
        - Hàm này được gọi trên thread file, nên chỉ ``notify``, không làm gì nặng.
        """
        raise NotImplementedError("TODO(C): ProgressReporter.update")

    @property
    def percent(self) -> int:
        """0–100 (size 0 counts as 100).

        Gợi ý:
        - File 0 byte: tránh chia cho 0 và coi như 100% (T-U34).
        - Toolbar đọc giá trị này mỗi 0.5 s.
        """
        raise NotImplementedError("TODO(C): ProgressReporter.percent")


@dataclass
class TransferInfo:
    """tid, direction ('send'|'recv'), filename, peer_name, size, done, state ('running'|'done'|'failed')."""

    tid: int
    direction: str
    filename: str
    peer_name: str
    size: int
    done: int = 0
    state: str = "running"


class TransferManager:
    """Runs file sends/receives on their own threads and tracks them for the toolbar."""

    # nội bộ: _lock, _active: dict[int, TransferInfo], _socks, _next_tid,
    #         _send_worker(info, path, ip, tcp_port), _check_meta(meta) -> (filename, size)

    def __init__(self, ident: Identity, downloads: Path, notify: Callable[[str], None],
                 stop_event: threading.Event) -> None:
        """Create downloads dir if missing; empty active table.

        Gợi ý:
        - Tạo thư mục ``downloads`` (kể cả thư mục cha) nếu chưa có. Mỗi instance có thể có thư mục riêng (D15).
        - Tạo ``_lock``, ``_active`` rỗng, ``_socks`` (để ``cancel_all`` đóng được), ``_next_tid`` bắt đầu từ 1.
        """
        raise NotImplementedError("TODO(C): TransferManager.__init__")

    def send_file(self, path: str, peer_name: str, ip: str, tcp_port: int) -> TransferInfo:
        """Validate in caller thread (exists, is file, <= MAX_FILE_SIZE), then start 'file-send-<tid>'; raise FileNotFoundError/ValueError.

        Gợi ý:
        - Kiểm tra trên ``MainThread`` để báo lỗi ngay cho người dùng (``[!] File not found: x.pdf``, T-M11), rồi mới tạo thread.
        - Cấp ``tid`` mới và đăng ký ``TransferInfo`` dưới khóa.
        - In ``[*] Sending slides.pdf (2.4 MB) to Minh ...`` rồi trả về ngay; KHÔNG chờ gửi xong (E4: chat vẫn chạy).
        - Phần 9.2 #4: chặn đuôi ``.exe`` hay đổi giới hạn 10 MB thì kiểm thêm ở đây (phía gửi).
        """
        raise NotImplementedError("TODO(C): send_file")

    def handle_incoming(self, sock: socket.socket, addr: tuple[str, int], meta: dict) -> None:
        """Run in the 'tcp-in' thread (renamed 'file-recv-<tid>'): validate meta, ACK/ERR, recv_stream to .part, verify, replace or delete.

        Gợi ý:
        - Theo đúng máy trạng thái file ở Phần 4.3 và sequence 3: kiểm meta → ``ACK ready`` hoặc ``ERR`` → nhận đúng ``size`` byte thô vào ``.part`` → chờ ``ACK sent``+sha256 → so khớp → ``os.replace`` → ``ACK done``.
        - Quá giới hạn → ``ERR too_large`` và KHÔNG tạo ``.part``, chưa nhận byte nào (T-U36). Sai hash → ``ERR checksum`` và xóa ``.part`` (T-U37).
        - Mọi nhánh lỗi/gián đoạn: ĐÓNG file rồi mới xóa ``.part`` (bắt buộc trên Windows, D14), không bao giờ để lại file final dở dang (T-U33).
        - Đặt ``FILE_IO_TIMEOUT`` cho socket. Đổi tên thread thành ``file-recv-<tid>``. Bỏ ``TransferInfo`` khỏi ``_active`` trong mọi trường hợp.
        - Thông báo ở cả đầu (``Receiving ...``) và kết quả (``Saved downloads/...`` hoặc ``interrupted — partial file deleted``).
        """
        raise NotImplementedError("TODO(C): handle_incoming — nhận file an toàn")

    def active(self) -> list[TransferInfo]:
        """Copies of running transfers (for toolbar and /threads).

        Gợi ý:
        - Copy dưới khóa. Toolbar gọi hàm này mỗi 0.5 s nên phải nhanh.
        """
        raise NotImplementedError("TODO(C): active")

    def cancel_all(self) -> None:
        """Close all transfer sockets (used on /quit); workers clean up their .part files.

        Gợi ý:
        - Chỉ đóng socket; việc dọn ``.part`` do chính thread worker làm khi nó thấy lỗi (tránh hai thread cùng xóa một file).
        - Copy danh sách socket dưới khóa, nhả khóa rồi mới đóng.
        - Test: T-M14, T-I09.
        """
        raise NotImplementedError("TODO(C): cancel_all")

    # ------------------------------------------------------------------ nội bộ
    def _send_worker(self, info: TransferInfo, path: str, ip: str, tcp_port: int) -> None:
        """Thread 'file-send-<tid>': dial a NEW TCP connection, FILE → ACK ready → raw bytes → ACK sent → wait ACK done.

        Gợi ý:
        - Mở kết nối TCP mới tới listen port của peer (D12), không dùng kết nối chat. Wireshark W5 phải thấy 2 ``tcp.stream``.
        - Nhận ``ERR`` thay vì ``ACK ready`` → in ``[!] Minh rejected slides.pdf: too_large``.
        - Gửi xong mà không nhận ``ACK done`` (ERR checksum, EOF, timeout) → báo thất bại kèm % đã gửi (``failed at 43%``).
        - Bọc toàn thân bằng ``try/except``/``finally``: luôn đóng file, đóng socket, bỏ khỏi ``_active``.
        - Kết quả thành công: ``... 100%  Done (SHA-256 OK)``.
        """
        raise NotImplementedError("TODO(C): _send_worker")

    def _check_meta(self, meta: dict) -> tuple[str, int]:
        """Validate FILE meta and return (safe filename, size); raise BadFrame or TransferError('too_large').

        Gợi ý:
        - Kiểm có đủ khóa, kiểu đúng (``size`` là số nguyên không âm), version.
        - Tên đi qua ``safe_filename`` trước khi dùng ở bất cứ đâu.
        - ``size > MAX_FILE_SIZE`` → lỗi ``too_large``. Phần 9.2 #4: giới hạn phía nhận sửa ở đây.
        - Bên gọi đổi lỗi thành frame ``ERR`` với ``code`` phù hợp.
        """
        raise NotImplementedError("TODO(C): _check_meta")
