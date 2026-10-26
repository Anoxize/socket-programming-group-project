"""Entry point của LAN Chat: ``python lanchat.py --name Quan``.

Mục đích: gọi ``parse_args``, tạo ``App``, chạy và trả exit code cho hệ điều hành.
Owner: Thành viên A.
Phục vụ yêu cầu: A6, L1; rubric: M8.
Được import (Phần 3.1): ``lanchat.app`` và ``lanchat.config``. Không import module nào khác.
Luồng chạy code ở đây (Phần 3.2): ``MainThread``.

Lưu ý: file này trùng tên với package ``lanchat/``. Khi chạy ``python lanchat.py``,
câu ``import lanchat`` vẫn lấy package vì Python ưu tiên thư mục có ``__init__.py``.
"""

from __future__ import annotations

from lanchat.app import App  # noqa: F401  (dùng khi viết main)
from lanchat.config import parse_args  # noqa: F401  (dùng khi viết main)


def main(argv: list[str] | None = None) -> int:
    """Parse CLI args, build App, run it, return process exit code.

    Gợi ý:
    - Lấy ``Settings`` từ ``parse_args(argv)``. Khi tham số sai, argparse tự in usage và thoát mã 2.
    - Tạo ``App(settings)`` rồi trả đúng giá trị ``App.run()`` trả về: 0 là bình thường, 2 là port TCP bận (T-M01).
    - Đừng bọc mọi exception để "giấu" lỗi. ``App.run`` đã gọi ``shutdown()`` trong ``finally``.
    - Nếu người dùng bấm Ctrl+C trước khi console kịp chạy, nên thoát gọn, không in traceback.
    - Test liên quan: T-M01, T-R02 (clone mới → làm theo README → chạy được).
    """
    raise NotImplementedError("TODO(A): main — parse_args, App, run")


if __name__ == "__main__":
    raise SystemExit(main())
