"""Phân tích dòng nhập và điều phối lệnh ``/list``, ``/chat``, ``/send``…

Mục đích: tách một dòng thành ``ParsedLine``, gọi đúng handler, lưu snapshot của lần
``/list`` gần nhất (D08), sinh text cho prompt và bottom toolbar.
Owner: Thành viên C.
Phục vụ yêu cầu: F1–F8, C1, J3, J5; rubric: M4.
Được import (Phần 3.1): ``config``, ``chat_manager``, ``peer_registry``, ``discovery``,
``file_transfer``. Không import ``ui`` (nhận ``notify``), ``connection`` hay ``app``.
Luồng chạy code ở đây (Phần 3.2):
- ``MainThread``: ``handle`` và mọi ``cmd_*`` (được ``Console.run`` gọi qua ``on_line``).
- Thread refresh của prompt_toolkit: ``prompt_text``, ``toolbar_text`` (mỗi 0.5 s).
Khóa: không có khóa riêng; dữ liệu chung được đọc qua method của từng đối tượng (khóa nằm bên trong method đó).
Phần 9.2 #3: thêm lệnh mới (``/whoami``, ``/history 10``, ``/clear``) = thêm ``cmd_<tên>`` vào
``_handlers`` và một dòng trong ``HELP_TEXT``.
"""

from __future__ import annotations

import threading  # noqa: F401  (cmd_threads dùng threading.enumerate)
from dataclasses import dataclass
from typing import Callable

from lanchat.chat_manager import ChatManager
from lanchat.config import Identity
from lanchat.discovery import Broadcaster
from lanchat.peer_registry import PeerRegistry
from lanchat.file_transfer import TransferManager, human_size  # noqa: F401

HELP_TEXT: str = """\
Commands:
  /list                    show online peers (numbered)
  /chat <name|number>      open or switch chat (e.g. /chat Minh, /chat 2, /chat Quan#3f9a)
  /send <file>             send a file to the current partner (quotes allowed)
  /leave                   close the current chat
  /status <online|away>    change your status
  /threads                 list running threads (debug)
  /help                    show this help
  /quit                    exit (Ctrl+D also quits)
Anything not starting with '/' is sent to the current partner."""


@dataclass(frozen=True)
class ParsedLine:
    """kind ('empty'|'text'|'command'), name (lower, no '/'), arg (rest of line, stripped)."""

    kind: str
    name: str = ""
    arg: str = ""


def parse_line(line: str) -> ParsedLine:
    """'/chat  Minh' -> command('chat','Minh'); 'hello' -> text; '' -> empty.

    Gợi ý:
    - Dòng chỉ có khoảng trắng là ``empty``. Dòng không bắt đầu bằng ``/`` là ``text`` (giữ nguyên nội dung, không strip phần giữa).
    - Tên lệnh viết thường (``/CHAT 2`` → ``chat``); nhiều khoảng trắng giữa lệnh và tham số vẫn đúng.
    - ``arg`` giữ nguyên dấu ngoặc kép: ``/send "my file.pdf"`` → việc bỏ ngoặc để ``cmd_send`` làm.
    - Test: T-U38 (parametrize).
    """
    raise NotImplementedError("TODO(C): parse_line")


class CommandDispatcher:
    """Maps parsed input lines to handlers; owns the last /list snapshot."""

    # nội bộ: _numbered: list[str] | None, _handlers: dict[str, Callable[[str], object]]

    def __init__(self, ident: Identity, registry: PeerRegistry, chat: ChatManager,
                 broadcaster: Broadcaster, transfers: TransferManager,
                 notify: Callable[[str], None]) -> None:
        """Build handler table {'list': cmd_list, ...}.

        Gợi ý:
        - Bảng ``_handlers`` ánh xạ tên lệnh → method ``cmd_*``. Thêm lệnh mới chỉ cần thêm một dòng ở đây.
        - ``_numbered = None`` cho tới khi người dùng gõ ``/list`` lần đầu (D08).
        """
        raise NotImplementedError("TODO(C): CommandDispatcher.__init__")

    def handle(self, line: str) -> bool:
        """Dispatch one input line; return False on /quit.

        Gợi ý:
        - ``text`` → ``chat.send_text``; ``empty`` → bỏ qua; ``command`` → tra ``_handlers``.
        - Lệnh lạ → ``[!] Unknown command '/foo'. Type /help`` (T-U39, J5).
        - Một handler ném lỗi không được làm chết vòng nhập: bắt, in ``[!] ...`` và tiếp tục.
        - Chỉ ``/quit`` trả ``False``; mọi trường hợp khác trả ``True``.
        """
        raise NotImplementedError("TODO(C): handle")

    def cmd_list(self, arg: str) -> None:
        """Print numbered online peers (name, IP, TCP port, status, unread); save snapshot.

        Gợi ý:
        - Lấy ``registry.snapshot()`` một lần, in theo đúng thứ tự đó và lưu danh sách peer_id vào ``_numbered`` (D08, ``test_list_saves_snapshot``).
        - Tên dùng ``display_name`` để thấy ``Quan#3f9a`` khi trùng (T-M18).
        - Không có ai online thì in một dòng thông báo thay cho bảng rỗng.
        - Đánh dấu partner hiện tại và số unread từng người (T-M02).
        """
        raise NotImplementedError("TODO(C): cmd_list")

    def cmd_chat(self, arg: str) -> None:
        """/chat <name|number> -> chat.open_chat(arg, self._numbered).

        Gợi ý:
        - Thiếu tham số → in usage ngắn (T-M13).
        - Phần còn lại (tra cứu, kết nối, thông báo) là việc của ``ChatManager.open_chat``.
        """
        raise NotImplementedError("TODO(C): cmd_chat")

    def cmd_send(self, arg: str) -> None:
        """/send <file> to current partner (quotes allowed); errors for no partner / missing file.

        Gợi ý:
        - Bỏ cặp ngoặc kép bao quanh nếu có (tên file có khoảng trắng).
        - Không có partner → ``No active chat`` hint; file không tồn tại → ``[!] File not found: x.pdf`` (T-M11, J3).
        - Lấy (name, ip, port) từ ``chat.partner_endpoint()`` rồi gọi ``transfers.send_file``; bắt ``FileNotFoundError``/``ValueError`` để in lỗi.
        """
        raise NotImplementedError("TODO(C): cmd_send")

    def cmd_leave(self, arg: str) -> None:
        """/leave -> chat.leave().

        Gợi ý:
        - Chỉ chuyển tiếp. Đừng lặp lại logic của ``ChatManager.leave`` ở đây.
        """
        raise NotImplementedError("TODO(C): cmd_leave")

    def cmd_status(self, arg: str) -> None:
        """/status <online|away> -> broadcaster.set_status().

        Gợi ý:
        - Giá trị không hợp lệ (``ValueError``) hoặc thiếu → in usage có liệt kê ``STATUSES`` (T-U39 ``test_status_usage``).
        - Thành công thì in xác nhận ngắn cho chính mình.
        """
        raise NotImplementedError("TODO(C): cmd_status")

    def cmd_help(self, arg: str) -> None:
        """Print HELP_TEXT.

        Gợi ý:
        - In qua ``notify``, không ``print`` trực tiếp.
        """
        raise NotImplementedError("TODO(C): cmd_help")

    def cmd_threads(self, arg: str) -> None:
        """Debug: list threading.enumerate() names (shows the thread model live).

        Gợi ý:
        - Dùng khi vấn đáp câu 9: phải thấy ``udp-broadcaster``, ``udp-listener``, ``tcp-acceptor``, ``recv-<tên>``, ``file-send-<tid>`` (T-M19).
        - Có thể in kèm daemon hay không để giải thích chiến lược shutdown.
        """
        raise NotImplementedError("TODO(C): cmd_threads")

    def cmd_quit(self, arg: str) -> bool:
        """Return False so Console.run stops.

        Gợi ý:
        - Không tự tắt mạng ở đây: ``App.run`` gọi ``shutdown()`` trong ``finally`` (Phần 3.4).
        """
        raise NotImplementedError("TODO(C): cmd_quit")

    def prompt_text(self) -> str:
        """'[Quan → Minh]> ' or '[Quan]> '.

        Gợi ý:
        - Được gọi mỗi 0.5 s từ thread của prompt_toolkit: phải rất nhanh và không bao giờ ném lỗi.
        - Yêu cầu phụ Phần 9.2: thêm ``(away)`` vào prompt thì sửa ở đây.
        """
        raise NotImplementedError("TODO(C): prompt_text")

    def toolbar_text(self) -> str:
        """'status: online | unread: Huy 2 | ↑ slides.pdf 45%'.

        Gợi ý:
        - Ghép từ ``broadcaster.status``, ``chat.unread_counts()`` và ``transfers.active()``; phần nào trống thì bỏ.
        - ``↑`` cho gửi, ``↓`` cho nhận. Giống ``prompt_text``: nhanh và không ném lỗi.
        """
        raise NotImplementedError("TODO(C): toolbar_text")
