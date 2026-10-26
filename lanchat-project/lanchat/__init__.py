"""Package chính của LAN Chat & File Sharing (CTT105 Mạng máy tính).

Owner: Thành viên A.
Phục vụ yêu cầu: A6, L1; rubric: M8.
Được import: không import module nào (file này chỉ khai báo phiên bản).
Luồng chạy code ở đây: không có (chỉ chạy một lần khi import).

Ghi chú: thư mục gốc có cả file ``lanchat.py`` (entry point) lẫn package
``lanchat/`` cùng tên. Khi ``import lanchat``, Python ưu tiên package (thư mục có
``__init__.py``), nên hai thứ không đè nhau. Đừng tạo thêm module tên ``lanchat``.
"""

from __future__ import annotations

__version__: str = "1.0.0"
