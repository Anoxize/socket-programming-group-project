"""Unit test cho ``lanchat/chat_manager.py`` (T-U24…T-U29).

Owner: Thành viên B. Phục vụ: D3, D4, F3, F5, J1, J5, H7; rubric M2.
Không mở mạng: dùng ``FakeConnectionManager`` dưới đây thay cho ConnectionManager thật,
``collect_notify`` (conftest) thay cho Console.notify, và một PeerRegistry thật đã nạp sẵn
vài Datagram.
"""

from __future__ import annotations

import pytest

from lanchat import chat_manager, peer_registry  # noqa: F401  (module được test)


class FakeConnectionManager:
    """Thay thế ConnectionManager trong test: ghi lại các lần connect/disconnect, không mở socket."""

    def __init__(self) -> None:
        """Create empty fake state.

        Gợi ý:
        - Giữ dict peer_id → kết nối giả, và list các lời gọi ``disconnect`` để test kiểm.
        - Kết nối giả chỉ cần các thuộc tính ``peer_id``, ``name``, ``ip``, ``tcp_port`` và ``send_msg`` ghi lại text đã gửi.
        """
        raise NotImplementedError("TODO(B): FakeConnectionManager.__init__")

    def connect(self, peer_id: str, ip: str, tcp_port: int):
        """Return a fake connection (create if missing).

        Gợi ý:
        - Có thể thêm cờ để giả lập ``ConnectError`` khi cần test nhánh lỗi.
        """
        raise NotImplementedError("TODO(B): FakeConnectionManager.connect")

    def get(self, peer_id: str):
        """Return the fake connection or None.

        Gợi ý:
        - Giống chữ ký của ConnectionManager.get.
        """
        raise NotImplementedError("TODO(B): FakeConnectionManager.get")

    def disconnect(self, peer_id: str, reason: str = "leave") -> bool:
        """Record the call and drop the fake connection.

        Gợi ý:
        - Trả True nếu có kết nối, False nếu không.
        """
        raise NotImplementedError("TODO(B): FakeConnectionManager.disconnect")


def test_msg_from_partner_shown(collect_notify):
    """T-U24 — on_frame MSG từ partner hiện tại (Minh) — Mong đợi: notify đúng '[Minh] ...'."""
    pytest.skip("TODO(B)")


def test_msg_from_other_counts_unread(collect_notify):
    """T-U25 — 2 MSG từ Huy trong khi partner là Minh — Mong đợi: notify '(1 unread)' rồi '(2 unread)'."""
    pytest.skip("TODO(B)")


def test_switch_replays_unread(collect_notify):
    """T-U26 — open_chat('Huy') sau khi có 2 tin chưa đọc — Mong đợi: 'Switched to Huy — 2 unread:', phát lại đúng 2 dòng, unread về 0."""
    pytest.skip("TODO(B)")


def test_send_without_partner_hint(collect_notify):
    """T-U27 — send_text khi chưa có partner — Mong đợi: hint '[!] No active chat. Use /list then /chat <name|number>'."""
    pytest.skip("TODO(B)")


def test_partner_bye_clears(collect_notify):
    """T-U28 — on_connection_closed(partner, 'leave') — Mong đợi: in 'left the chat' và partner_id trở thành None."""
    pytest.skip("TODO(B)")


def test_duplicate_close_silent(collect_notify):
    """T-U28 — on_connection_closed(conn, 'duplicate') — Mong đợi: không in gì, partner không đổi."""
    pytest.skip("TODO(B)")


def test_history_bounded(collect_notify):
    """T-U29 — đưa 600 dòng vào history của một peer — Mong đợi: chỉ giữ 500 dòng mới nhất (HISTORY_LIMIT)."""
    pytest.skip("TODO(B)")
