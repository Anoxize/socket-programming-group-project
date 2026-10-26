"""Integration test cho ``lanchat/discovery.py`` trên loopback broadcast (T-I08).

Owner: Thành viên B. Phục vụ: B1, B2, N3; rubric M1.
Chỉ chạy trên Linux (127.255.255.255 chưa chắc chạy trên Windows/macOS, rủi ro R4) và
được đánh dấu ``lan``. Dùng UDP port test riêng (khác 9999) để không đụng instance thật.
"""

from __future__ import annotations

import sys

import pytest

from lanchat import discovery, peer_registry  # noqa: F401  (module được test)


@pytest.mark.lan
@pytest.mark.skipif(sys.platform != "linux", reason="loopback broadcast 127.255.255.255 chỉ kiểm chắc trên Linux (R4)")
def test_two_instances_discover_each_other():
    """T-I08 — 2 cặp Broadcaster/Listener, bcast=127.255.255.255, UDP port test riêng — Mong đợi: mỗi registry thấy bên kia trong ≤ 4 s."""
    pytest.skip("TODO(B)")


@pytest.mark.lan
@pytest.mark.skipif(sys.platform != "linux", reason="loopback broadcast 127.255.255.255 chỉ kiểm chắc trên Linux (R4)")
def test_udp_bye_removes_peer():
    """T-I08 — một bên gọi send_bye() — Mong đợi: bên kia nhận OFFLINE(reason='bye') ngay, không phải chờ PEER_TIMEOUT."""
    pytest.skip("TODO(B)")
