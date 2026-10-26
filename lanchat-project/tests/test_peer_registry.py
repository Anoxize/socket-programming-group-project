"""Unit test cho ``lanchat/peer_registry.py`` (T-U15…T-U23).

Owner: Thành viên B. Phục vụ: B2, B3, B4, C2, F1, F2, H7; rubric M1.
Dùng ``fake_clock`` (conftest) để test timeout không cần sleep. Tạo Datagram bằng tay
(hoặc qua parse_datagram) với peer_id 8 hex khác nhau.
"""

from __future__ import annotations

import pytest

from lanchat import peer_registry  # noqa: F401  (module được test)


def test_new_peer_online_event(fake_clock):
    """T-U15 — handle_datagram với HELLO của peer mới — Mong đợi: trả về đúng một PeerEvent ONLINE."""
    pytest.skip("TODO(B)")


def test_repeat_hello_no_event(fake_clock):
    """T-U15 — gửi lại cùng HELLO sau khi advance thời gian — Mong đợi: trả [] và last_seen được cập nhật."""
    pytest.skip("TODO(B)")


def test_expire_after_timeout(fake_clock):
    """T-U16 — fake_clock t = 9.9 rồi t = 10.1, mỗi lần gọi expire() — Mong đợi: peer còn ở 9.9; ra OFFLINE(reason='timeout') ở 10.1 (dùng hằng PEER_TIMEOUT, không hard-code)."""
    pytest.skip("TODO(B)")


def test_status_change_event(fake_clock):
    """T-U17 — HELLO cùng peer, status đổi từ online sang away — Mong đợi: một PeerEvent STATUS."""
    pytest.skip("TODO(B)")


def test_ignore_self(fake_clock):
    """T-U18 — HELLO mang peer_id của chính mình — Mong đợi: bị bỏ qua, registry vẫn rỗng."""
    pytest.skip("TODO(B)")


def test_duplicate_names(fake_clock):
    """T-U19 — 2 peer cùng tên Quan — Mong đợi: display_name ra 'Quan#xxxx'; find('Quan') ném LookupError có gợi ý dùng số hoặc Quan#xxxx."""
    pytest.skip("TODO(B)")


def test_find_by_number_snapshot(fake_clock):
    """T-U20 — find('2', numbered=[...]) và trường hợp số trỏ tới peer đã bị xóa — Mong đợi: đúng peer; LookupError khi peer đã offline."""
    pytest.skip("TODO(B)")


def test_bye_removes_immediately(fake_clock):
    """T-U21 — handle_datagram với BYE của peer đang online — Mong đợi: xóa ngay, trả OFFLINE(reason='bye')."""
    pytest.skip("TODO(B)")


def test_restart_same_endpoint_replaces(fake_clock):
    """T-U22 — HELLO có peer_id mới nhưng cùng ip:port với entry cũ (D07) — Mong đợi: entry cũ bị thay, snapshot chỉ còn 1 dòng."""
    pytest.skip("TODO(B)")


def test_thread_safety_stress():
    """T-U23 — 8 thread cùng gọi handle_datagram và expire 1000 lần — Mong đợi: không exception, số peer cuối cùng nhất quán."""
    pytest.skip("TODO(B)")
