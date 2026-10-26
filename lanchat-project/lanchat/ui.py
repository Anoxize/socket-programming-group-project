"""Console: bọc prompt_toolkit (PromptSession + patch_stdout) và chế độ ``--plain``.

Mục đích: vòng nhập ở ``MainThread``; ``notify()`` an toàn khi gọi từ nhiều thread (có
khóa, chạy bên trong ``patch_stdout`` nên dòng in ra nằm phía trên dòng nhập và chữ đang
gõ dở được vẽ lại); prompt động; bottom toolbar; chế độ dự phòng ``--plain`` dùng
``input``/``print`` cho terminal trong IDE hoặc khi không phải TTY (D22).
Nền tảng: ``option_a_prompt_toolkit.py`` của giảng viên. So sánh với
``option_b_manual_redraw.py`` (vẽ lại thủ công ``\\r\\033[K``) trong báo cáo mục 4.4.
Owner: Thành viên C.
Phục vụ yêu cầu: A3, D3, G1, G2, G3, G4; rubric: M4.
Được import (Phần 3.1, quy tắc 3): KHÔNG import module nào của dự án; chỉ
``prompt_toolkit`` và thư viện chuẩn. Quy tắc 4: chỉ ``app.py`` biết tới ``Console``.
Luồng chạy code ở đây (Phần 3.2):
- ``MainThread``: ``run`` (block ở ``session.prompt()``).
- Mọi thread (``recv-*``, ``udp-listener``, ``file-*``…): ``notify``.
- Thread của prompt_toolkit (``patch-stdout-flush-thread``, refresh): gọi lại ``prompt_text``/``toolbar_text`` mỗi 0.5 s.
Khóa: ``_print_lock`` (cộng StdoutProxy của ``patch_stdout``).
"""

from __future__ import annotations

import threading  # noqa: F401  (dùng cho _print_lock)
from typing import Callable

from prompt_toolkit import PromptSession  # noqa: F401
from prompt_toolkit.patch_stdout import patch_stdout  # noqa: F401


class Console:
    """Thread-safe console around prompt_toolkit, with a plain fallback."""

    # nội bộ: _print_lock: threading.Lock, _session: PromptSession | None

    def __init__(self, prompt_text: Callable[[], str],
                 toolbar_text: Callable[[], str] | None = None, plain: bool = False) -> None:
        """Configure PromptSession (erase_when_done, bottom_toolbar, refresh_interval=0.5) or plain mode.

        Gợi ý:
        - ``prompt_text``/``toolbar_text`` là HÀM (callable), không phải chuỗi: prompt_toolkit gọi lại chúng nên số unread và % tự cập nhật (Phần 3.4).
        - ``erase_when_done`` để dòng đã gõ không bị in lặp (ChatManager tự echo ``[Quan] text``).
        - Plain mode: không tạo ``PromptSession`` (``_session = None``). Test T-U40 chạy ở chế độ này, không cần TTY.
        - Tạo ``_print_lock`` trong mọi chế độ.
        """
        raise NotImplementedError("TODO(C): Console.__init__")

    def notify(self, text: str) -> None:
        """Thread-safe: print text above the input line (holds _print_lock).

        Gợi ý:
        - Mọi output của chương trình đi qua đây (D22). Giữ khóa chỉ trong lúc in, không làm gì khác dưới khóa.
        - Mỗi lần gọi in nguyên một dòng; 10 thread × 100 dòng không được trộn chữ vào nhau (T-U40, G4).
        - Không bao giờ gọi ``prompt()`` từ đây. Hàm này được gọi từ thread mạng.
        - Nhớ flush khi ở plain mode.
        """
        raise NotImplementedError("TODO(C): Console.notify")

    def run(self, on_line: Callable[[str], bool], on_start: Callable[[], None] | None = None) -> None:
        """Enter patch_stdout, call on_start(), loop prompt(); Ctrl+C clears line, Ctrl+D = quit; stop when on_line returns False.

        Gợi ý:
        - Xem vòng lặp trong ``option_a_prompt_toolkit.py`` của thầy, nhưng khác ở chỗ: Ctrl+C chỉ xóa dòng đang gõ (tiếp tục), Ctrl+D mới là thoát.
        - Gọi ``on_start`` BÊN TRONG ``patch_stdout`` để các thread nền khởi động sau khi stdout đã được "vá" (G3).
        - ``on_line`` trả ``False`` (``/quit``) thì dừng vòng lặp.
        - Plain mode dùng ``input()``; hết input (EOF) cũng coi như quit.
        - Test: T-M06 (đang gõ dở, tin đến không làm vỡ dòng), T-M17 (``--plain``).
        """
        raise NotImplementedError("TODO(C): Console.run")
