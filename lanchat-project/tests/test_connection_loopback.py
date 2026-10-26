"""Integration test localhost cho ``lanchat/connection.py`` (T-I01…T-I07, T-I09, T-I10).

Owner: Thành viên A (T-I07 cùng C). Phục vụ: D1, D5, E4, J1, J2, F8, A5, H4, H5; rubric M2, M6.
Quy ước (Phần 5.3): mọi ConnectionManager dùng port 0 (hệ điều hành tự chọn port trống);
mọi test đặt timeout và đợi bằng ``threading.Event`` hoặc poll ≤ 2 s, KHÔNG dùng sleep cố định;
luôn ``close_all()`` trong teardown để không rò thread/port.
"""

from __future__ import annotations

import pytest

from lanchat import app, connection  # noqa: F401  (module được test)


def test_two_managers_exchange_msg():
    """T-I01 — 2 ConnectionManager (port 0), A connect tới B, gửi MSG hai chiều — Mong đợi: INTR thành công; on_frame của cả hai bên nhận đúng nội dung."""
    pytest.skip("TODO(A)")


def test_one_peer_many_connections():
    """T-I02 — A kết nối B và C cùng lúc, B và C gửi xen kẽ 50 MSG mỗi bên — Mong đợi: A nhận đủ 100 tin, đúng người gửi."""
    pytest.skip("TODO(A)")


def test_simultaneous_connect_tie_break():
    """T-I03 — A và B connect nhau đồng thời (threading.Barrier) — Mong đợi: sau ≤ 1 s mỗi bên còn đúng 1 kết nối và là cùng một kết nối (D03)."""
    pytest.skip("TODO(A)")


def test_connect_refused_fast():
    """T-I04 — connect tới port không có ai listen — Mong đợi: ConnectError trong ≤ 3.5 s."""
    pytest.skip("TODO(A)")


@pytest.mark.slow
def test_connect_unreachable_timeout():
    """T-I04 — connect tới IP không phản hồi (blackhole) — Mong đợi: ConnectError trong ≤ 3.5 s, không treo lâu hơn CONNECT_TIMEOUT."""
    pytest.skip("TODO(A)")


def test_peer_close_without_bye_is_lost():
    """T-I05 — B sock.close() không gửi BYE — Mong đợi: A nhận on_closed(reason='lost')."""
    pytest.skip("TODO(A)")


def test_peer_reset_is_lost():
    """T-I05 — B đóng kiểu RST (SO_LINGER 0) — Mong đợi: A nhận on_closed(reason='lost'), không exception lọt ra ngoài."""
    pytest.skip("TODO(A)")


def test_garbage_first_frame_rejected():
    """T-I06 — fake peer gửi rác làm frame đầu — Mong đợi: kết nối bị đóng (ERR not_intro/bad_frame), acceptor vẫn sống, kết nối hợp lệ tiếp theo vẫn được."""
    pytest.skip("TODO(A)")


@pytest.mark.slow
def test_silent_first_frame_timeout():
    """T-I06 — một client giữ kết nối im lặng 6 s (quá HANDSHAKE_TIMEOUT) — Mong đợi: bị đóng sau khoảng 5 s, acceptor vẫn nhận kết nối khác."""
    pytest.skip("TODO(A)")


@pytest.mark.slow
def test_file_does_not_block_chat():
    """T-I07 — gửi file 20 MB A→B trong khi B gửi A 1 MSG mỗi 50 ms — Mong đợi: mọi MSG tới trong lúc file đang chạy; file nhận được đúng SHA-256 (E4)."""
    pytest.skip("TODO(A+C)")


def test_app_shutdown_joins_threads():
    """T-I09 — App.shutdown() với port 0, chế độ plain — Mong đợi: mọi thread do app tạo kết thúc trong ≤ 3 s."""
    pytest.skip("TODO(A)")


def test_connect_wrong_peer_id():
    """T-I10 — connect tới đúng ip:port nhưng peer trả INTR có peer_id khác (peer đã khởi động lại) — Mong đợi: ConnectError('wrong peer')."""
    pytest.skip("TODO(A)")
