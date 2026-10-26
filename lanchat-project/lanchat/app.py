"""App: tạo và nối mọi thành phần, khởi động thread, tắt chương trình có thứ tự.

Mục đích: đây là nơi DUY NHẤT biết đến mọi module (Phần 3.1). Tạo các đối tượng, nối
callback (Listener → ChatManager.on_peer_event; ConnectionManager → ChatManager.on_frame/
on_connection_closed và TransferManager.handle_incoming), in dòng khởi động và shutdown
theo đúng thứ tự ở Phần 3.4.
Owner: Thành viên A.
Phục vụ yêu cầu: A5, A6, H1–H7, F8, J1; rubric: M6, M8.
Được import (Phần 3.1): ``config``, ``peer_registry``, ``discovery``, ``connection``,
``chat_manager``, ``file_transfer``, ``ui``, ``commands``. Không module nào khác được import ``app``
(trừ ``lanchat.py``).
Luồng chạy code ở đây (Phần 3.2): ``MainThread`` (``__init__``, ``run``, ``shutdown``).
``_install_excepthook`` cài hook được gọi trên bất kỳ thread nào bị exception chưa bắt.
Khóa: không có khóa riêng. ``stop_event`` (``threading.Event``) là cờ dừng cho mọi vòng lặp.
"""

from __future__ import annotations

import threading  # noqa: F401  (stop_event, excepthook)

from lanchat.chat_manager import ChatManager  # noqa: F401
from lanchat.commands import CommandDispatcher  # noqa: F401
from lanchat.config import Identity, Settings, new_peer_id  # noqa: F401
from lanchat.connection import ConnectionManager  # noqa: F401
from lanchat.discovery import Broadcaster, Listener, guess_local_ip, make_udp_socket  # noqa: F401
from lanchat.file_transfer import TransferManager  # noqa: F401
from lanchat.peer_registry import PeerRegistry  # noqa: F401
from lanchat.ui import Console  # noqa: F401


class App:
    """Composition root of one LAN Chat instance."""

    # nội bộ: _start_threads(), _print_banner(), _install_excepthook()

    def __init__(self, settings: Settings) -> None:
        """Create Identity, stop_event, UDP socket, registry, discovery threads, ConnectionManager, ChatManager, TransferManager, Console, CommandDispatcher; wire callbacks.

        Gợi ý:
        - Thứ tự tạo theo chiều phụ thuộc: tầng dưới trước (registry, discovery, connections) rồi tới ChatManager, TransferManager, Console, CommandDispatcher.
        - Có vòng "con gà quả trứng": ChatManager cần ``notify`` của Console, còn Console cần ``prompt_text`` của CommandDispatcher. Nghĩ cách phá vòng (vd. truyền lambda gọi trễ) và giải thích được khi vấn đáp.
        - Chưa start thread nào ở đây; chưa bind TCP (để ``run`` báo port bận đúng cách).
        - ``--debug`` thì cấu hình ``logging`` ghi ra ``lanchat-<name>.log``, không in ra console (D25).
        """
        raise NotImplementedError("TODO(A): App.__init__ — tạo và nối thành phần")

    def run(self) -> int:
        """Start TCP listener (exit 2 if port busy), start threads inside Console.run(on_start), print startup lines, loop; finally shutdown(); return 0.

        Gợi ý:
        - ``connections.start()`` ném ``OSError`` khi port bận → in thông báo rõ ràng và trả 2 (D21, T-M01).
        - Các thread nền khởi động trong ``on_start`` (tức là bên trong ``patch_stdout``).
        - ``shutdown()`` đặt trong ``finally`` để Ctrl+D, ``/quit`` hay exception đều tắt gọn.
        - Ba dòng khởi động phải khớp Phần 4.5.
        """
        raise NotImplementedError("TODO(A): App.run")

    def shutdown(self) -> None:
        """Idempotent: UDP BYE -> close_all('quit') -> cancel_all() -> stop_event.set() -> close sockets -> join threads (2 s).

        Gợi ý:
        - Theo đúng 7 bước ở Phần 3.4; thứ tự quan trọng (BYE phải đi trước khi đóng socket UDP).
        - Gọi hai lần không lỗi (idempotent). Một bước lỗi không được chặn các bước sau.
        - ``join(timeout=2)`` từng thread; daemon chỉ là lưới an toàn (vấn đáp câu 16).
        - Test: T-I09 (mọi thread do app tạo kết thúc trong ≤ 3 s), T-M14.
        """
        raise NotImplementedError("TODO(A): App.shutdown")

    # ------------------------------------------------------------------ nội bộ
    def _start_threads(self) -> None:
        """Start Broadcaster and Listener (TCP acceptor is started by ConnectionManager.start).

        Gợi ý:
        - Gọi từ ``on_start`` của ``Console.run``.
        - Giữ tham chiếu tới các thread để ``shutdown`` join được.
        """
        raise NotImplementedError("TODO(A): _start_threads")

    def _print_banner(self) -> None:
        """Print the three startup lines of Phần 4.5 via notify.

        Gợi ý:
        - ``[*] Listening on TCP port …`` / ``[*] Broadcasting presence on UDP port … (bcast …)`` / ``[*] You are … (id …). Type /help.``
        - Có thể thêm IP từ ``guess_local_ip`` để người dùng biết máy mình.
        """
        raise NotImplementedError("TODO(A): _print_banner")

    def _install_excepthook(self) -> None:
        """Install threading.excepthook that logs and notifies '[!] internal error in <thread>'.

        Gợi ý:
        - Exception trong thread mặc định chỉ in traceback ra stderr và có thể làm vỡ dòng nhập; hook này giúp lỗi không bị "nuốt" mà cũng không làm vỡ UI (quy tắc khóa 5).
        - Ghi traceback đầy đủ vào log, chỉ in một dòng ngắn ra console.
        """
        raise NotImplementedError("TODO(A): _install_excepthook")
