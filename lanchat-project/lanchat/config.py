"""Hằng số, cấu hình chạy (Settings), định danh cục bộ (Identity) và phân tích CLI.

Mục đích: gom mọi hằng số vào một chỗ. Khi được yêu cầu sửa live (Phần 9.2 #1:
đổi 3 s → 5 s, 10 s → 15 s, đổi port) chỉ cần đổi một dòng ở đây. Test phải dùng
các hằng này, không hard-code giá trị.
Owner: Thành viên B.
Phục vụ yêu cầu: A4, A6, B1, B3, N1, N3; rubric: M1, M8.
Được import (Phần 3.1): chỉ thư viện chuẩn (argparse, uuid, dataclasses, pathlib).
Đây là tầng thấp nhất: KHÔNG import module nào của dự án.
Luồng chạy code ở đây (Phần 3.2): ``MainThread`` gọi ``parse_args``/``new_peer_id``
lúc khởi động. Các hằng được mọi thread đọc, chỉ đọc nên không cần khóa.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# --- Hằng số (đặc tả, xem Phần 2.2 và Phần 4.4) ---------------------------------
UDP_PORT: int = 9999
DEFAULT_TCP_PORT: int = 5000
DEFAULT_BCAST: str = "255.255.255.255"
BROADCAST_INTERVAL: float = 3.0      # B1
PEER_TIMEOUT: float = 10.0           # B3
SWEEP_INTERVAL: float = 1.0          # chu kỳ quét timeout trong Listener
CONNECT_TIMEOUT: float = 3.0         # dial + chờ INTR trả lời
HANDSHAKE_TIMEOUT: float = 5.0       # bên accept chờ frame đầu
FILE_IO_TIMEOUT: float = 30.0
MAX_DATAGRAM: int = 512
MAX_NAME_LEN: int = 20
MAX_MSG_BYTES: int = 65_536
MAX_CONTROL_BYTES: int = 4_096
MAX_FILE_SIZE: int = 1 << 30         # 1 GiB
FILE_CHUNK: int = 65_536
HISTORY_LIMIT: int = 500
STATUSES: tuple[str, ...] = ("online", "away")


@dataclass(frozen=True)
class Settings:
    """Runtime options: name, tcp_port, udp_port, bcast, downloads (Path), plain, debug."""

    name: str
    tcp_port: int = DEFAULT_TCP_PORT
    udp_port: int = UDP_PORT
    bcast: str = DEFAULT_BCAST
    downloads: Path = Path("downloads")
    plain: bool = False
    debug: bool = False


@dataclass(frozen=True)
class Identity:
    """This instance's identity: peer_id, name, tcp_port."""

    peer_id: str
    name: str
    tcp_port: int


def new_peer_id() -> str:
    """Return a fresh 8-hex-char random id (uuid4().hex[:8]).

    Gợi ý:
    - Sinh mới mỗi lần chạy và không lưu xuống đĩa (D05). Restart thì peer_id đổi, xử lý ở D07.
    - Kết quả phải qua được bước kiểm peer_id trong ``parse_datagram``: đúng 8 ký tự ``0-9a-f``.
    - peer_id là khóa của registry, connections, history và unread. Tên chỉ là nhãn hiển thị.
    """
    raise NotImplementedError("TODO(B): new_peer_id")


def validate_name(name: str) -> str:
    """Strip and validate a display name (1–20 chars, no '|', no control chars); raise ValueError.

    Gợi ý:
    - Bỏ khoảng trắng hai đầu trước rồi mới kiểm. Hàm trả về tên đã làm sạch.
    - Giới hạn 1..``MAX_NAME_LEN`` tính theo KÝ TỰ. Độ dài MSG thì tính theo byte (D09), đừng lẫn hai thứ.
    - Từ chối ``|`` vì đó là dấu phân cách của datagram UDP (D11). Từ chối cả ký tự điều khiển (xuống dòng, tab, NUL…).
    - Tên tiếng Việt có dấu như ``Quân`` phải hợp lệ (T-U11).
    - ``parse_args`` và ``parse_datagram`` cùng dùng hàm này. Thông điệp ValueError nên ngắn, tiếng Anh.
    """
    raise NotImplementedError("TODO(B): validate_name")


def parse_args(argv: list[str] | None = None) -> Settings:
    """Parse --name (required), --port, --udp-port, --bcast, --downloads, --plain, --debug.

    Gợi ý:
    - Mặc định lấy từ các hằng ở trên. Bảng tùy chọn nằm ở README mục 6.
    - ``argv=None`` thì đọc ``sys.argv``. Test sẽ truyền list vào.
    - Kiểm tên bằng ``validate_name`` và port trong khoảng 1–65535. Sai thì báo qua argparse để thoát mã 2.
    - ``--downloads`` đổi thành ``Path``. Mỗi instance chạy chung một máy nên có thư mục riêng (D15, Phần 5.6).
    - Không mở socket, không tạo thư mục ở đây. Đó là việc của ``App`` và ``TransferManager``.
    """
    raise NotImplementedError("TODO(B): parse_args")
