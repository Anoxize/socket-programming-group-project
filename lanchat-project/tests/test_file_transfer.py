"""Unit test cho ``lanchat/file_transfer.py`` (T-U30…T-U37).

Owner: Thành viên C. Phục vụ: E1, E2, E3, J4, D14, D15; rubric M3, M6.
Dùng ``sock_pair`` (gửi trên một thread phụ, nhận trên thread test), ``tmp_downloads``
và ``collect_notify``. Không mở port mạng thật.
"""

from __future__ import annotations

import pytest

from lanchat import file_transfer  # noqa: F401  (module được test)

# Đầu vào của T-U30 (dữ liệu đặc tả). Kết quả mong đợi để nhóm tự điền khi viết test:
# chỉ còn basename an toàn, không rỗng, không phải tên dành riêng, giữ nguyên tiếng Việt.
SAFE_FILENAME_CASES = [
    pytest.param("../../x", id="traversal-slash"),
    pytest.param("..\\..\\x", id="traversal-backslash"),
    pytest.param("C:\\Windows\\a.txt", id="windows-abs-path"),
    pytest.param("", id="rong"),
    pytest.param("CON", id="windows-reserved"),
    pytest.param("a|b?.txt", id="ky-tu-cam"),
    pytest.param("báo cáo.pdf", id="tieng-viet"),
    pytest.param("/foo/bar/", id="chi-co-thu-muc"),
]


@pytest.mark.parametrize("name", SAFE_FILENAME_CASES)
def test_safe_filename(name):
    """T-U30 — safe_filename với từng tên nguy hiểm (../../x, ..\\..\\x, C:\\Windows\\a.txt, "", CON, a|b?.txt, báo cáo.pdf, /foo/bar/) — Mong đợi: chỉ còn basename an toàn, không rỗng, không chứa / hoặc \\, giữ nguyên tiếng Việt."""
    pytest.skip("TODO(C)")


def test_unique_path_collision(tmp_path):
    """T-U31 — unique_path khi tmp_path đã có 'a.txt' và 'a (1).txt.part' — Mong đợi: trả về 'a (2).txt'."""
    pytest.skip("TODO(C)")


def test_stream_roundtrip_sha256(sock_pair):
    """T-U32 — send_stream/recv_stream file 3 MB qua sock_pair (thread gửi riêng) — Mong đợi: SHA-256 hai bên bằng nhau; progress tăng dần và kết thúc đúng bằng size."""
    pytest.skip("TODO(C)")


def test_interrupted_deletes_part(sock_pair, tmp_downloads, collect_notify):
    """T-U33 — handle_incoming khi bên gửi close sau 50% dữ liệu — Mong đợi: file .part bị xóa, không có file final, có notify lỗi 'interrupted'."""
    pytest.skip("TODO(C)")


def test_zero_byte_file(sock_pair, tmp_downloads, collect_notify):
    """T-U34 — truyền file 0 byte — Mong đợi: file được lưu (rỗng) và ProgressReporter.percent = 100."""
    pytest.skip("TODO(C)")


def test_progress_reporter_steps(collect_notify):
    """T-U35 — ProgressReporter(step=25) gọi update 1000 lần tăng dần tới size — Mong đợi: in đúng 4 dòng (25/50/75/100%)."""
    pytest.skip("TODO(C)")


def test_rejects_too_large(sock_pair, tmp_downloads, collect_notify):
    """T-U36 — meta có size > MAX_FILE_SIZE — Mong đợi: bên nhận trả ERR too_large, chưa nhận byte dữ liệu nào, không có file .part."""
    pytest.skip("TODO(C)")


def test_checksum_mismatch_deletes_part(sock_pair, tmp_downloads, collect_notify):
    """T-U37 — bên gửi gửi ACK sent với sha256 sai — Mong đợi: bên nhận trả ERR checksum, .part bị xóa, không có file final."""
    pytest.skip("TODO(C)")
