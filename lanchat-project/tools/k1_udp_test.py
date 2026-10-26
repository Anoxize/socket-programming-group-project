"""Milestone K1 (01/11): thử UDP broadcast giữa 2 máy và trên loopback (rủi ro R4).

Owner: Thành viên B. Phục vụ: K1, N3, N4; chuẩn bị cho B1, B2.
Được import: chỉ thư viện chuẩn. KHÔNG import package ``lanchat``.
Luồng: ``MainThread`` (vai trò ``listen`` hoặc ``send``, mỗi tiến trình một vai).

Cách chạy dự kiến (đọc ``sys.argv`` thủ công, không cần argparse):
``python tools/k1_udp_test.py listen B`` và ``python tools/k1_udp_test.py send A [bcast]``.
Ghi kết quả từng OS (Windows/macOS/Linux, ``255.255.255.255`` và ``127.255.255.255``) vào README.
"""

from __future__ import annotations

import socket  # noqa: F401
import sys  # noqa: F401


def main() -> int:
    """Run as 'listen <name>' or 'send <name> [bcast]' to check that broadcasts arrive.

    Gợi ý:
    - Tái sử dụng ý tưởng của ``udp_broadcast_demo.py`` của thầy: cách tạo socket (đặt ``SO_REUSEADDR``, ``SO_REUSEPORT`` nếu có, ``SO_BROADCAST`` TRƯỚC ``bind``; bind ``""``) và định dạng ``HELLO|name|tcp_port|status``.
    - Chạy 2–3 listener trên cùng một máy để kiểm việc dùng chung port 9999.
    - Thử cả ``255.255.255.255``, địa chỉ directed (vd. ``192.168.1.255``) và ``127.255.255.255``; ghi lại cái nào chạy trên OS nào (R4).
    - Nếu không thấy gói: kiểm Windows Firewall (đúng profile), client isolation của Wi-Fi, nhiều card mạng (N4). Ghi vào ``docs/issues_log.md``.
    - In cả ``addr`` của gói nhận được để thấy port nguồn luôn là 9999 (vì sao ``parse_datagram`` không dùng ``addr[1]``).
    """
    raise NotImplementedError("TODO(B): k1 UDP broadcast test")


if __name__ == "__main__":
    raise SystemExit(main())
