"""Nguồn chân lý duy nhất của wire format: frame TCP và datagram UDP.

Mục đích: encode/decode frame TCP (header cố định 8 byte ``!4sI``), ``recv_exact``,
payload JSON, datagram UDP ``HELLO|...``/``BYE|...``. File này không có thread và
không có state, nên test 100% bằng pytest được (T-U01…T-U14).
Owner: Thành viên A (phần datagram UDP do B viết test ở ``test_udp_datagram.py``).
Phục vụ yêu cầu: I1, I2, I3, D2 (UTF-8), J1 (phát hiện EOF); rubric: M5.
Được import (Phần 3.1, quy tắc 1): CHỈ ``config``, ``struct``, ``json``, ``socket``
(cộng ``dataclasses`` để khai báo ``Frame``/``Datagram``). Không import module nào khác
của dự án.
Luồng chạy code ở đây (Phần 3.2): không có thread riêng. Hàm ở đây được gọi từ
``MainThread`` (gửi MSG/BYE), ``tcp-in-*``, ``recv-*``, ``file-send-*``,
``file-recv-*`` (đọc/ghi frame) và ``udp-broadcaster``/``udp-listener`` (datagram).
Vì không có state nên không cần khóa. Việc khóa ``send_lock`` là trách nhiệm của bên gọi.
Đặc tả đầy đủ: ``docs/protocol.md``.
"""

from __future__ import annotations

import json  # noqa: F401  (dùng khi viết encode_json/decode_json)
import socket
import struct
from dataclasses import dataclass

from lanchat.config import (  # noqa: F401  (dùng khi viết thân hàm)
    MAX_CONTROL_BYTES,
    MAX_DATAGRAM,
    MAX_MSG_BYTES,
    STATUSES,
    Identity,
    validate_name,
)

# --- Hằng số (đặc tả, Phần 4.3) ----------------------------------------------
HEADER: struct.Struct = struct.Struct("!4sI")   # 4 byte TYPE ASCII + uint32 big-endian LENGTH = 8 byte
T_INTRO: bytes = b"INTR"
T_MSG: bytes = b"MSG "
T_BYE: bytes = b"BYE "
T_FILE: bytes = b"FILE"
T_ACK: bytes = b"ACK "
T_ERR: bytes = b"ERR "

# type -> độ dài payload tối đa (bảng 4.3)
MAX_PAYLOAD: dict[bytes, int] = {
    T_INTRO: MAX_CONTROL_BYTES,
    T_MSG: MAX_MSG_BYTES,
    T_BYE: MAX_CONTROL_BYTES,
    T_FILE: MAX_CONTROL_BYTES,
    T_ACK: MAX_CONTROL_BYTES,
    T_ERR: MAX_CONTROL_BYTES,
}

PROTOCOL_VERSION: int = 1   # trường "v" trong INTR và FILE

# Mã lỗi hợp lệ trong frame ERR (bảng 4.3)
ERR_CODES: tuple[str, ...] = (
    "bad_frame", "not_intro", "version", "too_large", "checksum", "io_error", "wrong_peer",
)
BYE_REASONS: tuple[str, ...] = ("leave", "quit", "duplicate")


# --- Exception ---------------------------------------------------------------
class FrameError(Exception):
    """Base class for framing problems."""


class PeerClosed(FrameError):
    """Peer closed cleanly exactly at a frame boundary (recv returned b'' before any header byte)."""


class TruncatedFrame(FrameError):
    """Connection ended in the middle of a header or payload."""


class BadFrame(FrameError):
    """Unknown type, length over limit, or invalid payload (bad JSON / missing fields / bad version)."""


# --- Frame TCP ---------------------------------------------------------------
@dataclass(frozen=True)
class Frame:
    """One decoded TCP frame: ftype (4 bytes) and payload (bytes)."""

    ftype: bytes
    payload: bytes


def recv_exact(sock: socket.socket, n: int) -> bytes:
    """Loop on recv() until exactly n bytes; raise PeerClosed if 0 bytes read, TruncatedFrame if partial.

    Gợi ý:
    - TCP là luồng byte: một lần ``recv`` có thể trả ít hơn số byte xin (I3). Phải đọc đủ n byte bằng vòng lặp, mỗi lần chỉ xin phần còn thiếu.
    - ``recv`` trả ``b''`` nghĩa là peer đã đóng (EOF). Đây chính là lỗi của sample 01/02: chúng không kiểm EOF nên vòng lặp quay mãi.
    - Phân biệt hai trường hợp EOF: chưa đọc được byte nào thì ``PeerClosed``; đã đọc được một phần thì ``TruncatedFrame`` (T-U05, T-U06).
    - Gom các mảnh bằng ``bytearray`` hoặc list rồi nối một lần. Không cộng ``bytes`` liên tục trong vòng lặp.
    - Test: T-U03 (FakeSocket mỗi lần trả 1 byte), T-U05, T-U06.
    """
    raise NotImplementedError("TODO(A): recv_exact — đọc đủ n byte")


def encode_frame(ftype: bytes, payload: bytes) -> bytes:
    """Return 8-byte header + payload; raise ValueError for unknown type or oversize payload.

    Gợi ý:
    - Độ dài trong header là số BYTE của payload, không phải số ký tự (D09). ``'Xin chào Việt Nam'`` là 20 byte.
    - Kiểm ``ftype`` có trong ``MAX_PAYLOAD`` và độ dài không vượt giới hạn trước khi đóng gói. Phía gửi cũng phải chặn, không chỉ phía nhận.
    - Header đóng gói bằng ``HEADER``. Đối chiếu kết quả với các ví dụ hex ở bảng 4.3 (vd. MSG "Xin chào" → ``4d 53 47 20 00 00 00 09``).
    - Test: T-U01, T-U02.
    """
    raise NotImplementedError("TODO(A): encode_frame — header 8 byte + payload")


def send_frame(sock: socket.socket, ftype: bytes, payload: bytes) -> None:
    """sendall() one complete frame (caller must hold the socket's send lock).

    Gợi ý:
    - Dùng ``sendall``, không dùng ``send``: ``send`` có thể chỉ gửi một phần.
    - Gửi header và payload trong MỘT lần gọi để hai thread không chen vào giữa một frame (quy tắc khóa 3).
    - Hàm này KHÔNG tự lấy khóa. ``Connection.send`` giữ ``send_lock`` rồi mới gọi vào đây.
    - Để lỗi socket (``OSError``) nổi lên cho bên gọi xử lý, không nuốt lỗi.
    """
    raise NotImplementedError("TODO(A): send_frame — sendall một frame")


def recv_frame(sock: socket.socket) -> Frame:
    """Read and validate header, then read exactly <length> payload bytes.

    Gợi ý:
    - Làm theo đúng 6 bước "Cách phía nhận parse" ở Phần 4.3 (``docs/protocol.md``).
    - Kiểm loại frame và độ dài TRƯỚC khi đọc payload. Header báo 10 MB thì phải ném ``BadFrame`` ngay, không cấp phát (T-U07: FakeSocket chỉ được đọc đúng 8 byte).
    - MSG có độ dài 0 cũng là ``BadFrame``.
    - Không decode UTF-8/JSON ở đây. Bên dùng chỉ decode khi đã có frame đủ.
    - Test: T-U01…T-U08.
    """
    raise NotImplementedError("TODO(A): recv_frame — header rồi payload")


# --- Payload JSON ------------------------------------------------------------
def encode_json(obj: dict) -> bytes:
    """Compact UTF-8 JSON (separators=(',',':'), ensure_ascii=False).

    Gợi ý:
    - Dạng gọn (không khoảng trắng) để độ dài khớp các ví dụ byte ở bảng 4.3 (INTR = 58 byte, BYE leave = 18 byte).
    - ``ensure_ascii=False`` để tên tiếng Việt đi dưới dạng UTF-8 thật, không thành ``\\u00e2``.
    - Kết quả là ``bytes``, không phải ``str``.
    """
    raise NotImplementedError("TODO(A): encode_json")


def decode_json(payload: bytes, required: tuple[str, ...] = ()) -> dict:
    """Parse a JSON payload and check required keys; raise BadFrame on failure.

    Gợi ý:
    - Mọi kiểu lỗi (UTF-8 hỏng, JSON hỏng, không phải object/dict, thiếu khóa) đều đổi thành ``BadFrame``. Không để ``json.JSONDecodeError`` hay ``UnicodeDecodeError`` lọt ra.
    - Nếu có khóa ``"v"`` mà khác ``PROTOCOL_VERSION`` thì cũng là ``BadFrame`` (T-U09 với ``v=2``).
    - Thông điệp lỗi nên nói rõ thiếu khóa nào, để dễ debug bằng ``fake_peer.py``.
    - Test: T-U09.
    """
    raise NotImplementedError("TODO(A): decode_json + kiểm khóa bắt buộc")


def make_intro(ident: Identity) -> bytes:
    """INTR payload: {"v":1,"peer_id","name","tcp_port"}.

    Gợi ý:
    - Lấy dữ liệu từ ``Identity``. Thứ tự khóa nên giống ví dụ ở bảng 4.3 để so được với Wireshark.
    - Bên nhận sẽ gọi ``decode_json`` với đúng các khóa này trong ``required``.
    - Dùng ``encode_json`` để mọi payload JSON cùng một định dạng.
    """
    raise NotImplementedError("TODO(A): make_intro")


def make_msg(text: str) -> bytes:
    """MSG payload = UTF-8 bytes of text; raise ValueError if empty or > MAX_MSG_BYTES.

    Gợi ý:
    - MSG là text UTF-8 thô, không bọc JSON (bảng 4.3).
    - Giới hạn tính sau khi encode, theo byte (D09). Chặn ngay ở phía gửi.
    - Chuỗi rỗng là lỗi. Câu hỏi: chuỗi chỉ có khoảng trắng thì sao? Ghi quyết định vào ``design_decisions.md``.
    - Phần 9.2 #2: nếu muốn gửi kèm giờ của bên gửi thì sửa ở đây.
    - Test: T-U10.
    """
    raise NotImplementedError("TODO(A): make_msg")


def make_bye(reason: str) -> bytes:
    """BYE payload: {"reason": "leave"|"quit"|"duplicate"}.

    Gợi ý:
    - Chỉ chấp nhận lý do trong ``BYE_REASONS``. Lý do khác thì ``ValueError``.
    - ``duplicate`` dùng cho tie-break D03. Bên nhận loại này không in gì (T-U28).
    """
    raise NotImplementedError("TODO(A): make_bye")


def make_file_meta(ident: Identity, filename: str, size: int) -> bytes:
    """FILE payload: {"v":1,"peer_id","name","filename","size"}.

    Gợi ý:
    - ``filename`` chỉ là tên (basename) và có thể chứa ``|`` hay tiếng Việt vì nằm trong JSON (D10).
    - ``size`` tính bằng byte, phía nhận dùng để biết khi nào nhận đủ (Phần 4.3, máy trạng thái file).
    - Giữ payload dưới ``MAX_CONTROL_BYTES``.
    """
    raise NotImplementedError("TODO(A): make_file_meta")


def make_ack(**fields: object) -> bytes:
    """ACK payload, e.g. {"status":"ready"} / {"status":"sent","sha256":...} / {"status":"done"}.

    Gợi ý:
    - Ba bước ACK của giao thức file: ``ready`` → (dữ liệu thô) → ``sent`` + sha256 → ``done``.
    - Nên bắt buộc có khóa ``status``.
    """
    raise NotImplementedError("TODO(A): make_ack")


def make_err(code: str, message: str) -> bytes:
    """ERR payload: {"code","message"}.

    Gợi ý:
    - ``code`` thuộc ``ERR_CODES``. ``message`` là câu ngắn cho người đọc, ví dụ ``"File > 1 GiB"``.
    - Gửi ERR xong thì đóng kết nối. Bên nhận ERR in lỗi rồi đóng (Phần 4.3, bước 6).
    """
    raise NotImplementedError("TODO(A): make_err")


# --- Datagram UDP (Phần 4.2) -------------------------------------------------
@dataclass(frozen=True)
class Datagram:
    """Parsed UDP datagram: kind ('HELLO'|'BYE'), name, tcp_port, status (None for BYE), peer_id, ip."""

    kind: str
    name: str
    tcp_port: int
    status: str | None
    peer_id: str
    ip: str


def encode_hello(ident: Identity, status: str) -> bytes:
    """b'HELLO|<name>|<tcp_port>|<status>|<peer_id>' (UTF-8).

    Gợi ý:
    - Đối chiếu với ví dụ: ``HELLO|Quan|5000|online|3f9a1c2e`` dài 31 byte; tên ``Quân`` thì 32 byte.
    - Không có ký tự xuống dòng ở cuối.
    - ``status`` phải thuộc ``STATUSES``.
    - Test: T-U11.
    """
    raise NotImplementedError("TODO(A): encode_hello")


def encode_udp_bye(ident: Identity) -> bytes:
    """b'BYE|<name>|<tcp_port>|<peer_id>'.

    Gợi ý:
    - Gửi một lần khi ``/quit`` để bên kia báo offline ngay (D16, W6).
    - Ví dụ ``BYE|Quan|5000|3f9a1c2e`` dài 22 byte.
    - Test: T-U14.
    """
    raise NotImplementedError("TODO(A): encode_udp_bye")


def parse_datagram(data: bytes, src_ip: str) -> Datagram | None:
    """Validate and parse one datagram; return None for anything malformed (never raises).

    Gợi ý:
    - Làm theo 6 bước "Cách phía nhận parse" ở Phần 4.2. Tuyệt đối không ném exception: gói rác từ mạng không được làm chết thread ``udp-listener``.
    - Vẫn nhận HELLO dạng cũ 4 trường của ``udp_broadcast_demo.py``. Khi đó peer_id ghép từ ip và port (T-U13).
    - IP lấy từ tham số ``src_ip`` (``addr[0]`` của ``recvfrom``), không bao giờ dùng ``addr[1]``.
    - Kiểm port, status, tên (``validate_name``) và peer_id. Việc lọc gói của chính mình KHÔNG làm ở đây mà ở ``PeerRegistry``.
    - Test: T-U11…T-U14 (T-U12 có parametrize nhiều kiểu gói hỏng).
    """
    raise NotImplementedError("TODO(A): parse_datagram — không bao giờ ném lỗi")
