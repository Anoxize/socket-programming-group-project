# Đặc tả giao thức LAN Chat (v1)

> Owner: Thành viên A (mục 4.2 do B viết phần giải thích). Phục vụ: I1–I3, M5.
> Nguồn chân lý trong code: `lanchat/protocol.py`. Tài liệu này và code phải luôn khớp nhau:
> thêm loại frame mới (Phần 9.2 #5) thì sửa cả hai trong cùng một PR.


## 4.1 Tổng quan cổng và kênh

| Kênh | Transport | Cổng | Hướng | Nội dung |
|---|---|---|---|---|
| Discovery | UDP broadcast | 9999 (mọi peer dùng chung) | 1 gửi tới nhiều | `HELLO` mỗi 3 s, `BYE` khi thoát |
| Chat | TCP | listen port của peer nhận (mặc định 5000, đổi bằng `--port`) | hai chiều, lâu dài | `INTR`, `MSG `, `BYE `, `ERR ` |
| File | TCP (kết nối riêng cho mỗi file) | cùng listen port | gửi tới nhận, đóng sau khi xong | `FILE`, `ACK `, raw bytes, `ACK `, `ERR ` |

## 4.2 Datagram UDP

**Định dạng** (UTF-8, phân cách bằng `|`, không có newline, tối đa 512 byte):
```
HELLO|<name>|<tcp_port>|<status>|<peer_id>
BYE|<name>|<tcp_port>|<peer_id>
```

| Trường | Kiểu | Ràng buộc |
|---|---|---|
| type | ASCII | `HELLO` hoặc `BYE` |
| name | UTF-8 | 1–20 ký tự, không chứa `\|`, không có ký tự điều khiển |
| tcp_port | số thập phân | 1–65535 |
| status | ASCII | `online` hoặc `away` (chỉ có trong HELLO) |
| peer_id | hex | 8 ký tự `[0-9a-f]` |

**Ví dụ.** `HELLO|Quan|5000|online|3f9a1c2e` dài 31 byte:
```
48 45 4c 4c 4f 7c 51 75 61 6e 7c 35 30 30 30 7c 6f 6e 6c 69 6e 65 7c 33 66 39 61 31 63 32 65
H  E  L  L  O  |  Q  u  a  n  |  5  0  0  0  |  o  n  l  i  n  e  |  3  f  9  a  1  c  2  e
```
Với tên tiếng Việt `Quân`, ký tự `â` mã hóa thành 2 byte `c3 a2`, nên cả gói dài 32 byte. `BYE|Quan|5000|3f9a1c2e` dài 22 byte.

**Cách phía nhận parse** (`parse_datagram`). Hàm này không bao giờ ném exception, gói sai thì trả `None`:
1. Nếu `len(data) > MAX_DATAGRAM` thì bỏ.
2. `data.decode("utf-8")`. Lỗi decode thì bỏ.
3. `split("|")`. HELLO phải có 5 trường. Chấp nhận thêm dạng cũ 4 trường, khi đó `peer_id = f"{ip}:{port}"`. BYE phải có 4 trường. Sai số trường thì bỏ.
4. Kiểm tra port (là số, trong khoảng), status (thuộc `STATUSES`), name (`validate_name`) và peer_id.
5. Gắn `ip = addr[0]` lấy từ `recvfrom`. Không bao giờ dùng `addr[1]`, vì port nguồn luôn là 9999.
6. Bước lọc chính mình (`peer_id == my_peer_id`) nằm trong `PeerRegistry.handle_datagram`.

## 4.3 Frame TCP

**Header cố định 8 byte**, struct `"!4sI"` (network byte order, tức big-endian):
```
 0      1      2      3      4      5      6      7      8 ...
+------+------+------+------+------+------+------+------+---------------------+
|   TYPE (4 byte ASCII, đệm space)  |  LENGTH (uint32 big-endian) | PAYLOAD (LENGTH byte) |
+------+------+------+------+------+------+------+------+---------------------+
```

| TYPE | Kênh | Payload | Max LENGTH | Ý nghĩa |
|---|---|---|---|---|
| `INTR` | chat | JSON `{"v":1,"peer_id","name","tcp_port"}` | 4096 | frame đầu tiên, gửi cả hai chiều (D04) |
| `MSG ` | chat | text UTF-8 thô (không JSON), ≥ 1 byte | 65 536 | một tin nhắn |
| `BYE ` | chat | JSON `{"reason":"leave"\|"quit"\|"duplicate"}` | 4096 | đóng có báo trước |
| `FILE` | file | JSON `{"v":1,"peer_id","name","filename","size"}` | 4096 | frame đầu của kết nối file |
| `ACK ` | file | JSON `{"status":"ready"}` / `{"status":"sent","sha256"}` / `{"status":"done"}` | 4096 | các bước của giao thức file |
| `ERR ` | cả hai | JSON `{"code","message"}`, với code ∈ `bad_frame`, `not_intro`, `version`, `too_large`, `checksum`, `io_error`, `wrong_peer` | 4096 | báo lỗi rồi đóng |

**Ví dụ byte** (đã tính thật):

| Frame | Header (8 byte, hex) | Payload | Dài payload |
|---|---|---|---|
| MSG "Xin chào" | `4d 53 47 20 00 00 00 09` | `58 69 6e 20 63 68 c3 a0 6f` (`à` = `c3 a0`) | 9 |
| MSG "Xin chào Việt Nam" | `4d 53 47 20 00 00 00 14` | 17 ký tự nhưng **20 byte** | 20 |
| MSG "Chào Minh 👋" | `4d 53 47 20 00 00 00 0f` | emoji 👋 chiếm 4 byte `f0 9f 91 8b` | 15 |
| INTR | `49 4e 54 52 00 00 00 3a` | `{"v":1,"peer_id":"3f9a1c2e","name":"Quan","tcp_port":5000}` | 58 |
| BYE leave | `42 59 45 20 00 00 00 12` | `{"reason":"leave"}` | 18 |
| BYE quit | `42 59 45 20 00 00 00 11` | `{"reason":"quit"}` | 17 |
| FILE | `46 49 4c 45 00 00 00 51` | `{"v":1,"peer_id":"3f9a1c2e","name":"Quan","filename":"slides.pdf","size":2516582}` | 81 |
| ACK ready | `41 43 4b 20 00 00 00 12` | `{"status":"ready"}` | 18 |
| ERR too_large | `45 52 52 20 00 00 00 2d` | `{"code":"too_large","message":"File > 1 GiB"}` | 45 |

**Cách phía nhận parse** (`recv_frame`):
1. `hdr = recv_exact(sock, 8)`. Nếu chưa đọc được byte nào mà gặp `b''` thì ném `PeerClosed` (peer đóng sạch). Nếu đã đọc được 1–7 byte thì ném `TruncatedFrame`.
2. `ftype, n = HEADER.unpack(hdr)`. Nếu `ftype` không có trong `MAX_PAYLOAD` thì ném `BadFrame("unknown type")`.
3. Nếu `n > MAX_PAYLOAD[ftype]`, hoặc `ftype == MSG` mà `n == 0`, thì ném `BadFrame` **trước khi đọc payload**. Đây là cách chống cấp phát hàng GB khi header bị hỏng hoặc bị cố ý làm sai.
4. `payload = recv_exact(sock, n)`, vòng lặp `recv(n - len(buf))` (I3). Gặp EOF giữa chừng thì ném `TruncatedFrame`.
5. Trả về `Frame(ftype, payload)`. Việc decode UTF-8 hoặc JSON do phía dùng làm, và chỉ làm trên **frame đã đủ**.
6. Bên gọi xử lý: `BadFrame` thì gửi `ERR bad_frame` (nếu còn gửi được), đóng kết nối và notify. `PeerClosed` không kèm BYE thì báo "connection lost". `TruncatedFrame` cũng báo "connection lost".

**Máy trạng thái của kết nối chat:**
`ACCEPTED/DIALED` → (INTR qua lại trong vòng 5 s / 3 s) → `ESTABLISHED` (chỉ nhận `MSG `, `BYE `, `ERR `) → `CLOSED`.

**Máy trạng thái của kết nối file:**
`WAIT_FILE` → nhận `FILE` → `ACK ready` hoặc `ERR` → `STREAMING` (đúng `size` byte thô, **không có header**) → bên gửi gửi `ACK sent+sha256` → bên nhận trả `ACK done` hoặc `ERR checksum` → `CLOSED`. Socket file đặt timeout 30 s.

**Tại sao payload file là byte thô sau ACK ready:** vì kết nối dành riêng cho một file và kích thước đã biết trước, phía nhận chỉ cần đọc đúng `size` byte. Không mất 33% như base64 và không cần chia thành frame con.

## 4.4 Giới hạn tóm tắt

| Mục | Giá trị | Nằm ở |
|---|---|---|
| Datagram UDP | ≤ 512 byte | `config.MAX_DATAGRAM` |
| Tên | 1–20 ký tự | `config.MAX_NAME_LEN` |
| MSG | 1–65 536 byte UTF-8 | `config.MAX_MSG_BYTES` |
| Frame điều khiển (JSON) | ≤ 4096 byte | `config.MAX_CONTROL_BYTES` |
| File | ≤ 1 GiB | `config.MAX_FILE_SIZE` |
| Chunk file | 64 KiB | `config.FILE_CHUNK` |
| Tên file sau sanitize | ≤ 255 byte | `file_transfer.safe_filename` |

## 4.5 Thông điệp hiển thị chuẩn (dùng để đối chiếu khi test)

| Sự kiện | Chuỗi in ra |
|---|---|
| Khởi động | `[*] Listening on TCP port 5000` / `[*] Broadcasting presence on UDP port 9999 (bcast 255.255.255.255)` / `[*] You are Quan (id 3f9a1c2e). Type /help.` |
| Online / offline / status | `[+] Minh is online (192.168.1.12:6000)` / `[-] Minh went offline (timeout)` / `[*] Minh is now away` |
| Kết nối | `[*] Connecting to Minh ...` / `[*] Connected to Minh (192.168.1.12:6000)` |
| Đổi partner | `[*] Switched to Huy — 2 unread:`, sau đó là các dòng `[Huy] ...` |
| Tin nhắn | tin đến: `[Minh] text` / tin của mình: `[Quan] text` / tin của người khác: `[*] New message from Huy (2 unread)` |
| Đóng | `[*] Minh left the chat` / `[!] Connection to Minh lost` |
| File | `[*] Sending slides.pdf (2.4 MB) to Minh ... 25%` … `100%  Done (SHA-256 OK)` / `[*] Saved downloads/slides.pdf (2.4 MB)` |
| Lỗi | `[!] File not found: x.pdf` / `[!] Cannot connect to Minh: timed out` / `[!] No active chat. Use /list then /chat <name\|number>` / `[!] Unknown command '/foo'. Type /help` / `[!] Transfer slides.pdf interrupted at 43% — partial file deleted` / `[!] Protocol error from 192.168.1.20: bad frame — connection closed` |

## Lịch sử thay đổi

| Ngày | Phiên bản | Thay đổi | Người sửa |
|---|---|---|---|
| 26/10/2026 | v1 | Bản đầu, copy từ tài liệu thiết kế Phần 4 | A |
