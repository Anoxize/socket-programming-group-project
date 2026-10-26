"""Bảng peer online, có khóa bảo vệ, timeout và tra cứu theo tên/số.

Mục đích: logic thuần, không có socket. Nhận ``Datagram`` vào, trả ``list[PeerEvent]``
ra. Đồng hồ được inject từ ngoài (``clock``) nên test timeout không cần ``sleep``
(fixture ``fake_clock``).
Owner: Thành viên B.
Phục vụ yêu cầu: B2, B3, B4, C2, F1, F2, H7; rubric: M1.
Được import (Phần 3.1): ``config``, ``protocol`` (chỉ để lấy kiểu ``Datagram``).
Không import ``discovery``, ``chat_manager``, ``connection``, ``ui``.
Luồng chạy code ở đây (Phần 3.2):
- ``udp-listener`` ghi: ``handle_datagram``, ``expire``.
- ``MainThread`` đọc: ``snapshot``, ``find``, ``get``, ``display_name`` (``/list``, ``/chat``).
- ``ChatManager`` (chạy trên ``MainThread``/``recv-*``/``udp-listener``) đọc ``get``/``display_name``.
Khóa: ``self._lock`` (``threading.Lock``, KHÔNG dùng RLock, quy tắc 4). Mọi method công
khai trả BẢN SAO (copy) của ``Peer`` để bên ngoài không sửa được dữ liệu bên trong khi không giữ khóa.
"""

from __future__ import annotations

import threading  # noqa: F401  (dùng cho self._lock)
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable

from lanchat.config import PEER_TIMEOUT
from lanchat.protocol import Datagram


@dataclass
class Peer:
    """Known peer: peer_id, name, ip, tcp_port, status, first_seen, last_seen."""

    peer_id: str
    name: str
    ip: str
    tcp_port: int
    status: str
    first_seen: float
    last_seen: float


class PeerEventKind(Enum):
    """ONLINE, OFFLINE, STATUS."""

    ONLINE = "online"
    OFFLINE = "offline"
    STATUS = "status"


@dataclass(frozen=True)
class PeerEvent:
    """Change notification: kind, peer (copy), reason ('timeout'|'bye'|'replaced'|'')."""

    kind: PeerEventKind
    peer: Peer
    reason: str = ""


class PeerRegistry:
    """Thread-safe table of online peers keyed by peer_id."""

    # nội bộ: _lock: threading.Lock, _peers: dict[str, Peer]

    def __init__(self, my_peer_id: str, timeout: float = PEER_TIMEOUT,
                 clock: Callable[[], float] = time.monotonic) -> None:
        """Create empty registry; own peer_id is ignored by handle_datagram.

        Gợi ý:
        - Lưu ``my_peer_id``, ``timeout``, ``clock`` và tạo dict ``_peers`` rỗng cùng một ``threading.Lock``.
        - Mọi chỗ cần "thời điểm hiện tại" đều gọi ``self._clock()``, không gọi thẳng ``time.monotonic()``. Nhờ vậy T-U16 dùng ``fake_clock`` được.
        - Vì sao ``monotonic`` mà không phải ``time.time``? Ghi câu trả lời vào báo cáo mục 6.1.
        """
        raise NotImplementedError("TODO(B): PeerRegistry.__init__")

    def handle_datagram(self, dgram: Datagram) -> list[PeerEvent]:
        """Upsert on HELLO (ONLINE/STATUS events), remove on BYE; ignore own peer_id.

        Gợi ý:
        - Lọc chính mình theo peer_id, không theo tên hay IP (D05, T-U18).
        - HELLO lần đầu → ONLINE. HELLO lặp lại chỉ cập nhật ``last_seen``, không sinh sự kiện (T-U15). Status đổi → STATUS (T-U17).
        - D07: peer_id mới nhưng cùng (ip, tcp_port) với entry cũ → thay entry cũ, không để "ghost" (T-U22). Nên báo sự kiện gì cho người dùng? Chọn và ghi lại.
        - BYE → xóa ngay và trả OFFLINE(reason='bye') (T-U21).
        - Chỉ giữ khóa khi đọc/ghi dict. Tạo sự kiện chứa BẢN SAO của Peer, nhả khóa rồi mới return. Bên gọi sẽ in sau khi khóa đã nhả (quy tắc khóa 2).
        """
        raise NotImplementedError("TODO(B): handle_datagram — upsert/xóa + sinh PeerEvent")

    def expire(self) -> list[PeerEvent]:
        """Remove peers silent for > timeout; return OFFLINE(reason='timeout') events.

        Gợi ý:
        - So ``clock() - last_seen`` với ``timeout``. Lớn hơn hẳn mới xóa (T-U16: còn ở 9.9 s, mất ở 10.1 s).
        - Không xóa phần tử của dict trong lúc đang duyệt chính dict đó.
        - ``Listener`` gọi hàm này khoảng mỗi ``SWEEP_INTERVAL`` giây.
        """
        raise NotImplementedError("TODO(B): expire — quét timeout")

    def get(self, peer_id: str) -> Peer | None:
        """Return a copy of one peer or None.

        Gợi ý:
        - Trả bản sao (``dataclasses.replace`` hoặc tương tự) để bên ngoài không sửa vào bảng.
        - Lấy dưới khóa.
        """
        raise NotImplementedError("TODO(B): get")

    def snapshot(self) -> list[Peer]:
        """Copies of all peers sorted by (name.lower(), peer_id).

        Gợi ý:
        - Thứ tự sắp xếp phải tất định. ``/list`` và ``/chat <số>`` dựa vào nó (D08).
        - Copy dưới khóa, sắp xếp sau khi nhả khóa cũng được.
        """
        raise NotImplementedError("TODO(B): snapshot")

    def display_name(self, peer: Peer) -> str:
        """'Quan' or 'Quan#3f9a' when several online peers share the name.

        Gợi ý:
        - Chỉ thêm hậu tố ``#`` + 4 ký tự hex đầu của peer_id khi có từ 2 peer online cùng tên (D06, T-U19).
        - So tên không phân biệt hoa thường hay phân biệt? Thống nhất với ``find``.
        - Phần 9.2: hàm này được ``ChatManager`` dùng khi in thông báo.
        """
        raise NotImplementedError("TODO(B): display_name — thêm #xxxx khi trùng tên")

    def find(self, query: str, numbered: list[str] | None = None) -> Peer:
        """Resolve '2', 'Minh' or 'Minh#3f9a'; raise LookupError with a user-friendly message.

        Gợi ý:
        - Ba dạng đầu vào: số thứ tự, tên, tên kèm ``#xxxx``.
        - Số thứ tự tra trong ``numbered`` (danh sách peer_id của lần ``/list`` gần nhất, D08). Không có thì dùng ``snapshot()`` hiện tại. Số trỏ tới peer đã offline → ``LookupError`` (T-U20).
        - Tên trùng nhiều người → ``LookupError`` kèm gợi ý dùng số hoặc ``Tên#xxxx`` (T-U19).
        - Thông điệp lỗi sẽ được in thẳng ra màn hình, nên viết ngắn gọn bằng tiếng Anh như Phần 4.5.
        """
        raise NotImplementedError("TODO(B): find — số / tên / tên#id")

    def __len__(self) -> int:
        """Number of online peers.

        Gợi ý:
        - Đọc dưới khóa.
        """
        raise NotImplementedError("TODO(B): __len__")
