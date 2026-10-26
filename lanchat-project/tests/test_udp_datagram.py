"""Unit test cho datagram UDP trong ``lanchat/protocol.py`` (T-U11…T-U14).

Owner: Thành viên B. Phục vụ: I1, B2, B4; rubric M1, M6.
Không mở socket: chỉ gọi encode_hello / encode_udp_bye / parse_datagram.
"""

from __future__ import annotations

import pytest

from lanchat import protocol  # noqa: F401  (module được test)


def test_hello_roundtrip_vietnamese_name():
    """T-U11 — encode_hello với tên 'Quân' rồi parse_datagram(data, '192.168.1.10') — Mong đợi: mọi trường khớp, ip lấy từ tham số src_ip."""
    pytest.skip("TODO(B)")


# Các gói hỏng lấy từ T-U12 (dữ liệu đặc tả, không phải logic).
# Lưu ý: HELLO 4 trường KHÔNG phải gói hỏng (dạng cũ, xem T-U13), nên "thiếu trường"
# ở đây nghĩa là ít hơn 4 trường với HELLO, hoặc khác 4 trường với BYE.
GARBAGE_DATAGRAMS = [
    pytest.param(b"HELLO|Quan|5000", id="thieu-truong"),
    pytest.param(b"BYE|Quan|5000", id="bye-thieu-truong"),
    pytest.param(b"HELLO|Quan|abc|online|3f9a1c2e", id="port-abc"),
    pytest.param(b"HELLO|Quan|0|online|3f9a1c2e", id="port-0"),
    pytest.param(b"HELLO|Quan|70000|online|3f9a1c2e", id="port-70000"),
    pytest.param(b"HELLO|Quan|5000|busy|3f9a1c2e", id="status-busy"),
    pytest.param(b"HELLO|\xff\xfe|5000|online|3f9a1c2e", id="khong-phai-utf8"),
    pytest.param(b"HELLO|" + b"x" * 600, id="600-byte"),
    pytest.param(b"hello", id="chu-hello-tron"),
]


@pytest.mark.parametrize("data", GARBAGE_DATAGRAMS)
def test_parse_rejects_garbage(data):
    """T-U12 — parse_datagram với từng gói hỏng (thiếu trường, port abc/0/70000, status busy, không phải UTF-8, 600 byte, b"hello") — Mong đợi: trả None, không ném exception."""
    pytest.skip("TODO(B)")


def test_legacy_4_field_hello():
    """T-U13 — parse 'HELLO|A|5001|online' (dạng cũ của udp_broadcast_demo.py) — Mong đợi: được chấp nhận, peer_id = 'ip:5001'."""
    pytest.skip("TODO(B)")


def test_udp_bye():
    """T-U14 — parse 'BYE|Quan|5000|3f9a1c2e' — Mong đợi: kind == 'BYE', status là None."""
    pytest.skip("TODO(B)")
