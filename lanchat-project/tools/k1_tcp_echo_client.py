"""Milestone K1 (01/11): TCP echo client, gõ một dòng và nhận lại đúng dòng đó.

Owner: Thành viên A. Phục vụ: K1; chuẩn bị cho D1, J1, J2.
Được import: chỉ thư viện chuẩn. KHÔNG import package ``lanchat``.
Luồng: ``MainThread``.

Cách chạy dự kiến: ``python tools/k1_tcp_echo_client.py 192.168.1.12 5000``.
"""

from __future__ import annotations

import socket  # noqa: F401
import sys  # noqa: F401


def main() -> int:
    """Connect to host:port, send each typed line, print the echoed bytes, stop on EOF or empty line.

    Gợi ý:
    - Dựa trên ``01_client.py``/``02_client.py`` của thầy, nhưng sửa lỗi EOF: ``recv`` trả ``b''`` thì server đã đóng, phải dừng chứ không lặp mãi.
    - Đặt timeout khi connect để thấy rõ lỗi "refused" và "timed out" (chuẩn bị cho J2).
    - Thử gửi tiếng Việt có dấu và quan sát: số byte gửi ≠ số ký tự (D09). Ghi nhận xét vào ``issues_log.md`` nếu thấy lạ.
    - Thử gửi nhiều dòng thật nhanh: một ``recv`` có thể nhận gộp nhiều dòng. Đây là bằng chứng vì sao cần framing (I3).
    """
    raise NotImplementedError("TODO(A): k1 TCP echo client")


if __name__ == "__main__":
    raise SystemExit(main())
