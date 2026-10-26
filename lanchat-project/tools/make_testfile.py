"""Sinh file N MB dữ liệu ngẫu nhiên và in SHA-256 của nó (chuẩn bị demo /send).

Owner: Thành viên C. Phục vụ: M3, E1–E4 (T-M09, T-M10, demo phút 5:00–7:00).
Được import: chỉ thư viện chuẩn (``os``, ``hashlib``, ``sys``). KHÔNG import package ``lanchat``.
Luồng: ``MainThread``.

Cách chạy dự kiến: ``python tools/make_testfile.py 50`` → tạo ``test50.bin`` và in SHA-256.
"""

from __future__ import annotations

import hashlib  # noqa: F401
import os  # noqa: F401
import sys  # noqa: F401


def main() -> int:
    """Write <N> MiB of random bytes to test<N>.bin and print its size and SHA-256.

    Gợi ý:
    - Ghi theo từng khối (vd. 1 MiB) để không giữ cả 50 MB trong RAM; cập nhật SHA-256 song song.
    - Không ghi đè file đã có trừ khi người dùng yêu cầu (tránh mất file demo đã biết SHA).
    - In SHA-256 cùng định dạng với ``sha256sum``/``Get-FileHash`` để so nhanh lúc demo.
    - Dữ liệu ngẫu nhiên (không nén được) giúp ảnh Wireshark W5 và tốc độ truyền phản ánh đúng thực tế.
    """
    raise NotImplementedError("TODO(C): make_testfile")


if __name__ == "__main__":
    raise SystemExit(main())
