"""Fixture dùng chung cho toàn bộ test (Phần 5.3).

Owner: Thành viên C.
Phục vụ: M8 (pytest xanh), là nền cho T-U01…T-U40 và T-I01…T-I10.
Được import: chỉ thư viện chuẩn và ``pytest``. Không import module của dự án ở đây để
lỗi ở một module không làm hỏng việc thu thập (collect) mọi test.
Luồng: fixture chạy trên thread chính của pytest; ``FakeSocket`` có thể bị gọi từ thread phụ của test.

Cách dùng: test chỉ cần ghi tên fixture vào tham số, ví dụ ``def test_x(sock_pair): ...``.
Chừng nào fixture còn là stub thì test dùng nó sẽ hiện SKIPPED với lý do ``TODO(C): ...``.
"""

from __future__ import annotations

import socket  # noqa: F401  (dùng khi viết sock_pair)
from typing import Callable

import pytest


class FakeSocket:
    """Socket giả: ``recv(n)`` trả tối đa ``max_chunk`` byte mỗi lần và đếm tổng byte đã đọc.

    Dùng cho T-U03 (mỗi lần chỉ trả 1 byte) và T-U07 (kiểm chỉ đọc đúng 8 byte header).
    """

    def __init__(self, data: bytes, max_chunk: int = 1) -> None:
        """Store the bytes to serve and the per-recv chunk limit.

        Gợi ý:
        - Lưu dữ liệu, vị trí đọc hiện tại và bộ đếm ``bytes_read`` (test sẽ đọc thuộc tính này).
        - ``max_chunk`` mô phỏng TCP trả ít hơn số byte được xin.
        """
        raise NotImplementedError("TODO(C): FakeSocket.__init__")

    def recv(self, n: int) -> bytes:
        """Return at most min(n, max_chunk) bytes; b'' once the data is exhausted (EOF).

        Gợi ý:
        - Hết dữ liệu thì trả ``b''`` mãi mãi, giống socket thật khi peer đã đóng.
        - Cập nhật ``bytes_read`` mỗi lần trả dữ liệu.
        """
        raise NotImplementedError("TODO(C): FakeSocket.recv")

    def sendall(self, data: bytes) -> None:
        """Record sent bytes (optional, for tests that check what was written).

        Gợi ý:
        - Gom vào một buffer ``sent`` để test so sánh.
        """
        raise NotImplementedError("TODO(C): FakeSocket.sendall")


class FakeClock:
    """Đồng hồ giả cho ``PeerRegistry(clock=...)``: có ``.now`` và ``.advance(s)``."""

    def __init__(self, start: float = 0.0) -> None:
        """Start the clock at ``start`` seconds.

        Gợi ý:
        - Chỉ cần lưu giá trị ``now``.
        """
        raise NotImplementedError("TODO(C): FakeClock.__init__")

    def __call__(self) -> float:
        """Return current fake time (so the object itself can be passed as ``clock``).

        Gợi ý:
        - Trả ``self.now``.
        """
        raise NotImplementedError("TODO(C): FakeClock.__call__")

    def advance(self, seconds: float) -> None:
        """Move the fake time forward.

        Gợi ý:
        - T-U16 dùng ``advance`` để tới 9.9 s rồi 10.1 s mà không ``sleep``.
        """
        raise NotImplementedError("TODO(C): FakeClock.advance")


@pytest.fixture
def sock_pair():
    """Hai đầu của ``socket.socketpair()``, mỗi đầu ``settimeout(2)``; đóng cả hai sau test.

    Gợi ý:
    - Dùng ``yield`` để đóng socket trong phần teardown, kể cả khi test fail.
    - Timeout 2 s giúp test bị treo thì fail nhanh thay vì đứng mãi.
    - Dùng cho T-U01, T-U02, T-U04, T-U05, T-U06, T-U32.
    """
    pytest.skip("TODO(C): fixture sock_pair")


@pytest.fixture
def fake_socket() -> type[FakeSocket]:
    """Trả về lớp ``FakeSocket`` để test tự tạo: ``fake_socket(data, max_chunk=1)``.

    Gợi ý:
    - Chỉ cần trả lớp; để fixture thay vì import trực tiếp từ conftest (pytest khuyên không import conftest).
    """
    pytest.skip("TODO(C): fixture fake_socket (FakeSocket)")


@pytest.fixture
def fake_clock() -> FakeClock:
    """Đối tượng ``FakeClock`` bắt đầu ở t = 0.

    Gợi ý:
    - Truyền thẳng đối tượng vào ``PeerRegistry(..., clock=fake_clock)``.
    """
    pytest.skip("TODO(C): fixture fake_clock")


@pytest.fixture
def collect_notify() -> tuple[list[str], Callable[[str], None]]:
    """Trả ``(lines, notify)``: ``notify(text)`` append vào ``lines`` để test so chuỗi.

    Gợi ý:
    - Thay cho ``Console.notify`` trong test ChatManager/TransferManager/CommandDispatcher.
    - Nếu test có nhiều thread cùng gọi, cân nhắc thêm khóa cho list.
    - So với các chuỗi chuẩn ở Phần 4.5.
    """
    pytest.skip("TODO(C): fixture collect_notify")


@pytest.fixture
def tmp_downloads(tmp_path):
    """Thư mục ``downloads`` tạm (con của ``tmp_path``) cho test truyền file.

    Gợi ý:
    - Tạo thư mục con rồi trả ``Path``. pytest tự dọn ``tmp_path``.
    - Dùng cho T-U31, T-U33, T-U34, T-U36, T-U37, T-I07.
    """
    pytest.skip("TODO(C): fixture tmp_downloads")
