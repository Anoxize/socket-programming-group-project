"""Unit test cho ``lanchat/commands.py`` (T-U38, T-U39 và snapshot /list theo D08).

Owner: Thành viên C. Phục vụ: F1–F8, J5, C1; rubric M4.
Dùng ``collect_notify``. Với CommandDispatcher có thể dùng registry thật và các đối tượng
giả đơn giản cho ChatManager / Broadcaster / TransferManager.
"""

from __future__ import annotations

import pytest

from lanchat import commands  # noqa: F401  (module được test)

# Đầu vào của T-U38 (dữ liệu đặc tả). Kết quả mong đợi để nhóm tự điền khi viết test.
PARSE_LINE_CASES = [
    pytest.param("/chat  Minh", id="hai-khoang-trang"),
    pytest.param("/CHAT 2", id="chu-hoa"),
    pytest.param("hello", id="text"),
    pytest.param("   ", id="chi-khoang-trang"),
    pytest.param('/send "my file.pdf"', id="ngoac-kep"),
]


@pytest.mark.parametrize("line", PARSE_LINE_CASES)
def test_parse_line(line):
    """T-U38 — parse_line với '/chat  Minh', '/CHAT 2', 'hello', '   ', '/send "my file.pdf"' — Mong đợi: kind, name, arg đúng (command/chat/Minh; command/chat/2; text; empty; command/send/"my file.pdf")."""
    pytest.skip("TODO(C)")


def test_unknown_command_help(collect_notify):
    """T-U39 — handle('/foo') và handle('/help') — Mong đợi: "[!] Unknown command '/foo'. Type /help"; /help in HELP_TEXT; handle trả True."""
    pytest.skip("TODO(C)")


def test_status_usage(collect_notify):
    """T-U39 — handle('/status busy') — Mong đợi: in usage liệt kê online|away, status không đổi."""
    pytest.skip("TODO(C)")


def test_list_saves_snapshot(collect_notify):
    """D08 (bổ trợ T-U20) — cmd_list rồi một peer offline, sau đó /chat 2 — Mong đợi: _numbered giữ đúng thứ tự của lần /list; số trỏ tới peer đã offline thì báo lỗi."""
    pytest.skip("TODO(C)")
