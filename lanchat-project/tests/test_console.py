"""Unit test cho ``lanchat/ui.py`` (T-U40).

Owner: Thành viên C. Phục vụ: G4, H7; rubric M4.
Chạy Console ở chế độ plain (không cần TTY) và bắt output bằng ``capsys``.
"""

from __future__ import annotations

import pytest

from lanchat import ui  # noqa: F401  (module được test)


def test_notify_threadsafe_plain(capsys):
    """T-U40 — Console(plain=True), 10 thread mỗi thread notify 100 dòng — Mong đợi: đủ 1000 dòng nguyên vẹn, không dòng nào bị trộn chữ."""
    pytest.skip("TODO(C)")
