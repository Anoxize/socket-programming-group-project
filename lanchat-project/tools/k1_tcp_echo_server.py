"""Milestone K1 (01/11): TCP echo server tối giản để kiểm kết nối giữa 2 máy.

Owner: Thành viên A. Phục vụ: K1; chuẩn bị cho D1, J1.
Được import: chỉ thư viện chuẩn (``socket``, ``sys``). KHÔNG import package ``lanchat``:
công cụ K1 phải chạy được trước khi có code chính.
Luồng: chạy trên ``MainThread`` (một client mỗi lần là đủ cho K1).

Cách chạy dự kiến: ``python tools/k1_tcp_echo_server.py 5000``
(đọc port từ ``sys.argv`` cho đơn giản, không cần argparse).
"""

from __future__ import annotations

import socket  # noqa: F401
import sys  # noqa: F401


def main() -> int:
    """Listen on ('', port), accept clients one by one, echo back every chunk until EOF.

    Gợi ý:
    - Xuất phát từ ``01_server.py``/``02_server.py`` của thầy NHƯNG sửa hai lỗi: bind ``""`` thay vì ``127.0.0.1`` (để máy khác vào được), và kiểm EOF đúng kiểu Python 3 (``recv`` trả ``b''`` là peer đã đóng; so với chuỗi ``""`` như trong sample là sai vì bytes ≠ str, vòng lặp sẽ quay mãi).
    - In địa chỉ client khi ``accept`` và khi client đóng, để chụp làm minh chứng K1.
    - Echo bằng ``sendall``, không dùng ``send``.
    - Đóng socket trong ``finally``; Ctrl+C thoát gọn.
    """
    raise NotImplementedError("TODO(A): k1 TCP echo server")


if __name__ == "__main__":
    raise SystemExit(main())
