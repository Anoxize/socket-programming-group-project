"""Client TCP "thô" để test lỗi giao thức: gửi INTR/MSG đúng, gửi rác, đóng giữa chừng.

Owner: Thành viên A. Phục vụ: M6, J1, J2, I2 (T-I06, T-N03, T-N04 và demo lỗi).
Được import: có thể import ``lanchat.protocol`` và ``lanchat.config`` để dựng frame đúng
(và cố ý làm sai). Không import ``connection``/``app``: công cụ này phải độc lập với lõi đang test.
Luồng: ``MainThread``.

Kịch bản dự kiến (chọn bằng ``sys.argv``, không cần argparse), ví dụ:
``python tools/fake_peer.py <ip> <port> garbage | intro | half-header | half-payload | silent | huge-length``.
"""

from __future__ import annotations

import socket  # noqa: F401
import sys  # noqa: F401


def main() -> int:
    """Connect to a running lanchat and play one misbehaving scenario, printing what comes back.

    Gợi ý:
    - Mỗi kịch bản ứng với một nhánh lỗi trong Phần 4.3: frame đầu không phải INTR, header 3 byte rồi đóng, header báo 100 byte nhưng gửi 10, im lặng quá ``HANDSHAKE_TIMEOUT``, length 10 MB, đóng kiểu RST (``SO_LINGER`` 0).
    - In mọi byte nhận lại dạng hex để so với ERR mong đợi (``ERR not_intro``, ``ERR bad_frame``).
    - Sau mỗi kịch bản, app đích phải VẪN chạy và nhận được kết nối hợp lệ tiếp theo (T-I06, T-N03).
    - Có thể tái sử dụng các hàm ``make_*``/``encode_frame`` của ``protocol.py`` để dựng frame hợp lệ, rồi sửa vài byte để tạo frame hỏng.
    """
    raise NotImplementedError("TODO(A): fake_peer scenarios")


if __name__ == "__main__":
    raise SystemExit(main())
