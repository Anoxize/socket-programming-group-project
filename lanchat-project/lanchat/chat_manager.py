"""Trạng thái hội thoại: partner hiện tại, history theo peer, bộ đếm unread, thông báo.

Mục đích: đây là nơi định dạng mọi thông báo chat và online/offline (chuỗi chuẩn ở
Phần 4.5). Được ``MainThread`` gọi qua ``commands`` và được các thread mạng gọi qua
callback ``on_frame``/``on_connection_closed``/``on_peer_event``.
Owner: Thành viên B (A duyệt phần liên quan tới kết nối).
Phục vụ yêu cầu: D2, D3, D4, D5, F2, F3, F5, B4, C2, H7, J1, J2, J5; rubric: M2.
Được import (Phần 3.1): ``config``, ``protocol``, ``peer_registry``, ``connection``.
Không import ``ui`` (quy tắc 4: chỉ nhận ``notify: Callable[[str], None]``), không import
``commands``/``file_transfer``/``app``.
Luồng chạy code ở đây (Phần 3.2):
- ``MainThread``: ``open_chat``, ``send_text``, ``leave``, ``partner_id``, ``partner_endpoint``, ``unread_counts``, ``history``.
- ``recv-<name>``: ``on_frame``, ``on_connection_closed``.
- ``udp-listener``: ``on_peer_event``.
Khóa: ``self._lock`` (Lock thường) bảo vệ ``_partner``, ``_history``, ``_unread``. Quy tắc:
không gửi mạng và không ``notify`` khi đang giữ khóa; copy dữ liệu ra, nhả khóa, rồi mới gửi/in.
Test dùng ``FakeConnectionManager`` (trong ``tests/test_chat_manager.py``) thay cho ConnectionManager thật.
"""

from __future__ import annotations

import threading  # noqa: F401  (dùng cho self._lock)
from collections import deque  # noqa: F401  (dùng cho _history)
from dataclasses import dataclass
from typing import Callable

from lanchat.config import HISTORY_LIMIT, Identity  # noqa: F401
from lanchat.connection import ConnectError, Connection, ConnectionManager  # noqa: F401
from lanchat.peer_registry import PeerEvent, PeerEventKind, PeerRegistry  # noqa: F401
from lanchat.protocol import T_MSG, Frame  # noqa: F401


@dataclass(frozen=True)
class ChatLine:
    """One chat line: ts (epoch), sender_name, text, incoming (bool)."""

    ts: float
    sender_name: str
    text: str
    incoming: bool


class ChatManager:
    """Conversation state shared by the main thread and network threads."""

    # nội bộ: _lock, _partner, _history: dict[str, deque[ChatLine]], _unread: dict[str, int],
    #         _format_line(line: ChatLine) -> str

    def __init__(self, ident: Identity, registry: PeerRegistry,
                 connections: ConnectionManager, notify: Callable[[str], None]) -> None:
        """Empty state; notify is Console.notify.

        Gợi ý:
        - Lưu các phụ thuộc và tạo ``_lock``, ``_partner = None``, ``_history``, ``_unread`` rỗng.
        - History mỗi peer giới hạn ``HISTORY_LIMIT`` dòng (D19, T-U29). Chọn cấu trúc dữ liệu tự bỏ dòng cũ.
        - Khóa của history/unread là peer_id, không phải tên (D05).
        """
        raise NotImplementedError("TODO(B): ChatManager.__init__")

    # --- main thread ---------------------------------------------------------
    def open_chat(self, query: str, numbered: list[str] | None = None) -> None:
        """Resolve peer, connect if needed, set partner; print Connected/Switched + replay unread.

        Gợi ý:
        - Tra peer bằng ``registry.find(query, numbered)``. ``LookupError`` thì in thông điệp của nó với tiền tố ``[!]``.
        - In ``[*] Connecting to X ...`` TRƯỚC khi dial vì dial có thể mất tới 3 s. ``ConnectError`` → ``[!] Cannot connect to X: <lý do>`` (T-M12).
        - Kết nối mới → ``Connected to X (ip:port)``; kết nối có sẵn và có unread → ``Switched to X — k unread:`` rồi phát lại đúng các dòng chưa đọc, sau đó unread = 0 (T-U26).
        - Không giữ ``_lock`` trong lúc ``connections.connect`` (quy tắc khóa 1).
        - Các kết nối cũ vẫn giữ nguyên khi đổi partner (D01).
        """
        raise NotImplementedError("TODO(B): open_chat")

    def send_text(self, text: str) -> None:
        """Send MSG to current partner and echo '[me] text'; hint if no partner; handle send failure.

        Gợi ý:
        - Chưa có partner → ``[!] No active chat. Use /list then /chat <name|number>`` (D20, T-U27).
        - Gửi thành công mới echo ``[Quan] text`` và lưu history (incoming=False).
        - Gửi lỗi (``ConnectionError``) → báo mất kết nối, bỏ partner. Tin quá dài (``ValueError``) → báo lỗi, giữ partner.
        - Partner đang ``away`` thì in thêm gợi ý ``(Minh is away)`` (D17).
        """
        raise NotImplementedError("TODO(B): send_text")

    def leave(self) -> None:
        """/leave: BYE + close current partner's connection, clear partner.

        Gợi ý:
        - Không có partner thì in hint, không lỗi.
        - Gọi ``connections.disconnect(peer_id, "leave")`` sau khi đã nhả ``_lock`` (D02).
        - Phần 9.2 (yêu cầu phụ): nếu đổi ``/leave`` thành chỉ bỏ chọn partner thì sửa ở đây.
        - Test: T-M08.
        """
        raise NotImplementedError("TODO(B): leave")

    @property
    def partner_id(self) -> str | None:
        """peer_id of the current partner or None.

        Gợi ý:
        - Đọc dưới khóa. Prompt và toolbar gọi hàm này thường xuyên.
        """
        raise NotImplementedError("TODO(B): partner_id")

    def partner_endpoint(self) -> tuple[str, str, int] | None:
        """(name, ip, tcp_port) of current partner from its Connection (used by /send).

        Gợi ý:
        - Lấy từ ``Connection`` (``tcp_port`` là listen port của peer), không lấy port nguồn.
        - Partner đã mất kết nối thì trả ``None`` để ``/send`` báo lỗi.
        """
        raise NotImplementedError("TODO(B): partner_endpoint")

    def unread_counts(self) -> dict[str, int]:
        """peer display name -> unread count (copy).

        Gợi ý:
        - Khóa bên trong là peer_id; đổi sang tên hiển thị (``registry.display_name``) SAU khi đã copy ra và nhả khóa.
        - Bỏ các peer có 0 unread. Toolbar dùng kết quả này.
        """
        raise NotImplementedError("TODO(B): unread_counts")

    def history(self, peer_id: str, n: int = 20) -> list[ChatLine]:
        """Last n lines with that peer (copy).

        Gợi ý:
        - Trả list mới. Phần 9.2 #3: lệnh ``/history n`` sẽ gọi hàm này.
        """
        raise NotImplementedError("TODO(B): history")

    # --- callbacks từ thread mạng -------------------------------------------
    def on_frame(self, conn: Connection, frame: Frame) -> None:
        """Handle MSG: print now if from partner, else store + '[*] New message from X (k unread)'.

        Gợi ý:
        - Chạy trên thread ``recv-<name>``: phải nhanh, không gọi ``prompt()``, không chặn.
        - Decode UTF-8 ở đây (frame đã đủ). Byte lỗi thì xử lý sao cho không làm chết thread.
        - Lưu history cho mọi tin. Tin không phải từ partner thì tăng unread và in thông báo có số đếm (T-U25).
        - Cập nhật state dưới khóa, nhả khóa rồi mới ``notify`` (quy tắc khóa 1 và 2).
        - Phần 9.2 #5: frame loại mới (``TYPN``…) xử lý ở đây.
        """
        raise NotImplementedError("TODO(B): on_frame")

    def on_connection_closed(self, conn: Connection, reason: str) -> None:
        """Print 'left the chat' / 'connection lost'; clear partner if it was this peer; silent for 'duplicate'.

        Gợi ý:
        - ``leave``/``quit`` → ``[*] X left the chat``; ``lost`` → ``[!] Connection to X lost`` (Phần 4.5).
        - ``duplicate`` (tie-break D03) → không in gì và không đụng tới partner (T-U28).
        - Nếu kết nối đóng là của partner hiện tại thì bỏ partner (J1).
        - Mất kết nối TCP KHÔNG có nghĩa là peer offline (D16): không xóa khỏi registry.
        """
        raise NotImplementedError("TODO(B): on_connection_closed")

    def on_peer_event(self, event: PeerEvent) -> None:
        """Print '[+] X is online', '[-] X went offline (timeout|quit)', '[*] X is now away'.

        Gợi ý:
        - Chạy trên thread ``udp-listener``.
        - OFFLINE có ``reason='bye'`` in là ``(quit)``; ``timeout`` in ``(timeout)`` (Phần 4.5, sequence 1).
        - Online in kèm ``ip:port`` để đối chiếu với ``/list``.
        - Dùng ``registry.display_name`` để tên trùng hiện ``Quan#3f9a``.
        """
        raise NotImplementedError("TODO(B): on_peer_event")

    # --- nội bộ --------------------------------------------------------------
    def _format_line(self, line: ChatLine) -> str:
        """Format one chat line for display, e.g. '[Minh] hi'.

        Gợi ý:
        - Dạng chuẩn: ``[Tên] text`` cho cả tin đến và tin của mình (Phần 4.5).
        - Phần 9.2 #2: thêm giờ ``[14:03]`` từ ``line.ts`` thì chỉ sửa ở đây. Mọi chỗ in tin nhắn phải đi qua hàm này.
        - Yêu cầu phụ: hiện IP người gửi cũng sửa ở đây.
        """
        raise NotImplementedError("TODO(B): _format_line")
