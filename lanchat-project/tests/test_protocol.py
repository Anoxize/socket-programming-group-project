"""Unit test cho framing TCP trong ``lanchat/protocol.py`` (T-U01…T-U10).

Owner: Thành viên A. Phục vụ: I2, I3, D2, J1; rubric M5.
Mọi test dùng ``sock_pair`` hoặc ``fake_socket`` (conftest), không mở mạng thật.
Thay ``pytest.skip(...)`` bằng thân test thật khi viết xong hàm tương ứng.
"""

from __future__ import annotations

import pytest

from lanchat import protocol  # noqa: F401  (module được test)


def test_roundtrip_msg_ascii(sock_pair):
    """T-U01 — encode_frame(T_MSG, b"hello") gửi qua sock_pair rồi recv_frame — Mong đợi: Frame nhận được giống hệt (ftype và payload)."""
    pytest.skip("TODO(A)")


def test_vietnamese_length_is_bytes(sock_pair):
    """T-U02 — gửi MSG 'Xin chào Việt Nam' — Mong đợi: trường length trong header = 20 (byte, không phải 17 ký tự); decode ra đúng chuỗi."""
    pytest.skip("TODO(A)")


def test_emoji_length(sock_pair):
    """T-U02 — gửi MSG 'Chào Minh 👋' — Mong đợi: length = 15 (emoji chiếm 4 byte f0 9f 91 8b); decode ra đúng chuỗi."""
    pytest.skip("TODO(A)")


def test_fragmented_one_byte_per_recv(fake_socket):
    """T-U03 — FakeSocket mỗi lần recv chỉ trả 1 byte — Mong đợi: recv_frame vẫn trả về frame đúng."""
    pytest.skip("TODO(A)")


def test_coalesced_two_frames_one_send(sock_pair):
    """T-U04 — một sendall(f1 + f2) chứa hai frame — Mong đợi: gọi recv_frame hai lần được f1 rồi f2, không dính nhau."""
    pytest.skip("TODO(A)")


def test_peer_closed_mid_header(sock_pair):
    """T-U05 — gửi 3 byte header rồi close — Mong đợi: TruncatedFrame."""
    pytest.skip("TODO(A)")


def test_peer_closed_mid_payload(sock_pair):
    """T-U05 — header báo 100 byte, chỉ gửi 10 byte payload rồi close — Mong đợi: TruncatedFrame."""
    pytest.skip("TODO(A)")


def test_clean_close_raises_peer_closed(sock_pair):
    """T-U06 — close ngay đúng ranh giới frame (chưa gửi byte header nào) — Mong đợi: PeerClosed."""
    pytest.skip("TODO(A)")


def test_oversize_length_rejected_before_payload(fake_socket):
    """T-U07 — header báo length = 10 MB — Mong đợi: BadFrame, và FakeSocket ghi nhận chỉ đọc đúng 8 byte (chưa đọc payload)."""
    pytest.skip("TODO(A)")


def test_unknown_type_rejected(fake_socket):
    """T-U08 — header có type b"XXXX" — Mong đợi: BadFrame."""
    pytest.skip("TODO(A)")


def test_json_missing_fields():
    """T-U09 — decode_json cho INTR/FILE thiếu trường, JSON hỏng, v=2 — Mong đợi: BadFrame cho cả ba trường hợp."""
    pytest.skip("TODO(A)")


def test_make_msg_limits():
    """T-U10 — make_msg("") và make_msg("a" * 70000) — Mong đợi: ValueError cả hai (D09: chặn ở phía gửi)."""
    pytest.skip("TODO(A)")
