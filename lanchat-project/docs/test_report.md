# Báo cáo kiểm thử

> Owner: Thành viên C (mỗi owner tự điền dòng của mình). Phục vụ: K5, M6, M7.
> Cách điền: chạy test ở đúng mốc, ghi kết quả quan sát vào cột **Thực tế** (ngắn, có số liệu nếu được),
> cột **Đạt?** ghi ✅ / ❌ / ⚠️ (đạt một phần). Lỗi tìm được → ghi vào `issues_log.md` và trỏ ID test ở đó.

**Quy ước loại test:** U = unit pytest; I = integration localhost (cùng tiến trình pytest, port 0); M1 = thủ công nhiều instance trên 1 máy; M2 = thủ công trên 2 máy thật; N = netcat; W = Wireshark; R = review/checklist.

**Mốc:** K1 (01/11), K2 (08/11), K3 (15/11), K4 (22/11), K5 (29/11–06/12).

## Tóm tắt lần chạy

| Lần | Ngày | Commit / tag | `pytest -q` (passed / skipped / failed) | Người chạy | Ghi chú |
|---|---|---|---|---|---|
| 1 |  |  |  |  |  |

## 1. Ma trận test (Phần 5.1)

| ID | Mã YC / rubric | Loại | Bước | Kết quả mong đợi | Owner | Mốc | Thực tế | Đạt? |
|---|---|---|---|---|---|---|---|---|
| T-U01 | I2, M5 | U | `encode_frame(T_MSG, b"hello")` → `recv_frame` qua `sock_pair` | Frame giống hệt | A | K2 |  |  |
| T-U02 | I2, D2 | U | gửi `'Xin chào Việt Nam'` và `'Chào Minh 👋'` | header length = 20 và 15; decode ra đúng chuỗi | A | K2 |  |  |
| T-U03 | I3 | U | `FakeSocket` mỗi lần `recv` chỉ trả 1 byte | `recv_frame` vẫn trả frame đúng | A | K2 |  |  |
| T-U04 | I3 | U | một `sendall(f1+f2)` chứa hai frame | gọi `recv_frame` hai lần được f1 rồi f2 | A | K2 |  |  |
| T-U05 | I3, J1 | U | gửi 3 byte header rồi close; gửi header báo 100 byte, 10 byte payload rồi close | `TruncatedFrame` cả hai trường hợp | A | K2 |  |  |
| T-U06 | J1 | U | close ngay đúng ranh giới frame | `PeerClosed` | A | K2 |  |  |
| T-U07 | M5, M6 | U | header báo length = 10 MB | `BadFrame`, chưa đọc payload (FakeSocket ghi nhận số byte đã đọc là 8) | A | K2 |  |  |
| T-U08 | M5 | U | type `b"XXXX"` | `BadFrame` | A | K2 |  |  |
| T-U09 | M5 | U | INTR/FILE thiếu trường, JSON hỏng, `v=2` | `BadFrame` | A | K2 |  |  |
| T-U10 | D9, I2 | U | `make_msg("")`, `make_msg("a"*70000)` | `ValueError` | A | K2 |  |  |
| T-U11 | I1, B2 | U | `encode_hello` với tên `Quân` → `parse_datagram` | các trường khớp, `ip` lấy từ tham số | B | K2 |  |  |
| T-U12 | I1, M6 | U | parametrize: thiếu trường, port `abc`/`0`/`70000`, status `busy`, byte không phải UTF-8, 600 byte, `b"hello"` | trả `None`, không ném lỗi | B | K2 |  |  |
| T-U13 | I1 | U | `HELLO\|A\|5001\|online` (dạng cũ) | được chấp nhận, peer_id = `ip:5001` | B | K2 |  |  |
| T-U14 | I1, B4 | U | parse `BYE\|Quan\|5000\|3f9a1c2e` | `kind == "BYE"` | B | K2 |  |  |
| T-U15 | B2, B4 | U | HELLO mới, rồi HELLO lặp lại | lần 1 ra `[ONLINE]`, lần 2 ra `[]` và last_seen được cập nhật | B | K2 |  |  |
| T-U16 | B3, B4 | U | `fake_clock`: t = 9.9 rồi t = 10.1, gọi `expire()` | còn ở 9.9; ra `OFFLINE(timeout)` ở 10.1 | B | K2 |  |  |
| T-U17 | C2 | U | HELLO cùng peer, status đổi từ online sang away | `[STATUS]` | B | K2 |  |  |
| T-U18 | B2 | U | HELLO có peer_id của chính mình | bị bỏ qua | B | K2 |  |  |
| T-U19 | D06, F2 | U | 2 peer cùng tên Quan | `display_name` ra `Quan#xxxx`; `find("Quan")` ném `LookupError` có gợi ý | B | K2 |  |  |
| T-U20 | F1, F2, D08 | U | `find("2", numbered=[...])`; số trỏ tới peer đã bị xóa | đúng peer; `LookupError` | B | K2 |  |  |
| T-U21 | B4, D16 | U | gửi BYE | xóa ngay, `OFFLINE(bye)` | B | K2 |  |  |
| T-U22 | D07 | U | peer_id mới, cùng ip:port | entry cũ bị thay, chỉ còn 1 dòng | B | K2 |  |  |
| T-U23 | H7 | U | 8 thread cùng gọi `handle_datagram` và `expire` 1000 lần | không exception, số peer nhất quán | B | K3 |  |  |
| T-U24 | D3 | U | `on_frame` MSG từ partner (FakeConnectionManager) | notify `[Minh] ...` | B | K3 |  |  |
| T-U25 | D4 | U | 2 MSG từ Huy khi partner là Minh | notify `(1 unread)`, rồi `(2 unread)` | B | K3 |  |  |
| T-U26 | D4 | U | `open_chat("Huy")` | `Switched to Huy — 2 unread:`, phát lại 2 dòng, unread về 0 | B | K3 |  |  |
| T-U27 | J5, F3, D20 | U | `send_text` khi chưa có partner | hint `[!] No active chat...` | B | K3 |  |  |
| T-U28 | F5, J1 | U | `on_connection_closed(partner, "leave")`; `"duplicate"` | in "left the chat" và bỏ partner; với duplicate thì không in | B | K3 |  |  |
| T-U29 | H7, D19 | U | 600 dòng history | chỉ giữ 500 | B | K3 |  |  |
| T-U30 | E3, D15 | U | parametrize `safe_filename`: `../../x`, `..\\..\\x`, `C:\\Windows\\a.txt`, `""`, `CON`, `a\|b?.txt`, `báo cáo.pdf`, `/foo/bar/` | chỉ còn basename an toàn, không rỗng, giữ nguyên tiếng Việt | C | K3 |  |  |
| T-U31 | E3 | U | `unique_path` với `tmp_path` đã có `a.txt` và `a (1).txt.part` | ra `a (2).txt` | C | K3 |  |  |
| T-U32 | E1, E2, E3 | U | `send_stream`/`recv_stream` file 3 MB qua `sock_pair` (thread gửi) | SHA-256 hai bên bằng nhau; progress tăng dần và kết thúc đúng bằng size | C | K4 |  |  |
| T-U33 | J4 | U | `handle_incoming` với bên gửi close sau 50% | `.part` bị xóa, không có file final, có notify lỗi | C | K4 |  |  |
| T-U34 | E1 | U | file 0 byte | lưu được, percent = 100 | C | K4 |  |  |
| T-U35 | E2 | U | `ProgressReporter(step=25)` cập nhật 1000 lần | in đúng 4 dòng (25/50/75/100) | C | K4 |  |  |
| T-U36 | M6 | U | meta có size > MAX_FILE_SIZE | trả `ERR too_large`, chưa nhận byte nào, không có `.part` | C | K4 |  |  |
| T-U37 | D14 | U | bên gửi gửi sha sai | `ERR checksum`, `.part` bị xóa | C | K4 |  |  |
| T-U38 | F1–F8 | U | `parse_line`: `/chat  Minh`, `/CHAT 2`, `hello`, `   `, `/send "my file.pdf"` | kind, name, arg đúng | C | K2 |  |  |
| T-U39 | J5, F7, C1 | U | `handle("/foo")`, `handle("/status busy")`, `handle("/help")` | in gợi ý ngắn / usage / bảng lệnh | C | K2 |  |  |
| T-U40 | G4 | U | `Console(plain=True)`, 10 thread mỗi thread `notify` 100 dòng, dùng capsys | 1000 dòng nguyên vẹn, không bị trộn | C | K2 |  |  |
| T-I01 | D1, A5, H4, H5 | I | 2 `ConnectionManager` (port 0), A `connect` tới B, gửi MSG hai chiều | INTR thành công; cả hai `on_frame` nhận đúng nội dung | A | K3 |  |  |
| T-I02 | D5, M2 | I | A kết nối B và C cùng lúc, B và C gửi xen kẽ 50 MSG | A nhận đủ 100 tin, đúng người gửi | A | K3 |  |  |
| T-I03 | D03 | I | A và B `connect` nhau đồng thời (`threading.Barrier`) | sau 1 s mỗi bên còn đúng 1 kết nối và cùng là một kết nối | A | K3 |  |  |
| T-I04 | J2 | I | `connect` tới port không có ai listen; tới IP không phản hồi (đánh dấu `slow`) | `ConnectError` trong ≤ 3.5 s, UI không bị treo lâu hơn | A | K3 |  |  |
| T-I05 | J1 | I | B `sock.close()` không gửi BYE; B `shutdown` kiểu RST (`SO_LINGER 0`) | A nhận `on_closed(reason="lost")` | A | K3 |  |  |
| T-I06 | M6, I2 | I | `fake_peer` gửi rác làm frame đầu; một peer giữ kết nối im lặng 6 s | kết nối bị đóng (ERR not_intro / timeout), acceptor vẫn sống, kết nối hợp lệ tiếp theo vẫn được | A | K3 |  |  |
| T-I07 | E4 | I | gửi file 20 MB A→B trong khi B gửi A 1 MSG mỗi 50 ms | mọi MSG tới trong lúc file đang chạy; file đúng SHA | A + C | K4 |  |  |
| T-I08 | B1, B2, N3 | I | 2 cặp Broadcaster/Listener, `bcast=127.255.255.255`, UDP port test riêng (`@mark.lan`, Linux) | mỗi registry thấy bên kia trong ≤ 4 s; BYE thì biến mất ngay | B | K3 |  |  |
| T-I09 | F8 | I | `App.shutdown()` (port 0, chế độ plain) | mọi thread do app tạo đều kết thúc trong ≤ 3 s | A | K5 |  |  |
| T-I10 | J2, D04 | I | connect tới đúng ip:port nhưng peer_id khác (peer khởi động lại) | `ConnectError("wrong peer")` | A | K3 |  |  |
| T-M01 | A6, N1, D21 | M1 | chạy `--name Quan`, rồi chạy instance thứ 2 cùng `--port 5000` | in 3 dòng khởi động; instance 2 báo port bận và thoát với mã 2 | A | K2 |  |  |
| T-M02 | B1, B2, F1, A4, K2 | M2 | 2 máy và 1 instance phụ (`--port 5001`), gõ `/list` | thấy nhau trong ≤ 3 s; `/list` có số, tên, IP, port, status | B | K2 |  |  |
| T-M03 | B3, B4, D16 | M1/M2 | kill tiến trình Minh (đóng terminal); trường hợp khác Minh gõ `/quit` | kill: offline sau 10–11 s; quit: offline ngay | B | K2 |  |  |
| T-M04 | C1, C2, F6, D17 | M2 | `/status away` rồi `/status online` | bên kia in `is now away` trong ≤ 1 s; `/list` cập nhật | B | K2 |  |  |
| T-M05 | D1, F2, F3 | M2 | `/chat Minh`, `/chat 2`, gõ tin hai chiều | `Connected to Minh (ip:port)`; tin hiển thị đúng | A | K3 |  |  |
| T-M06 | D3, G1–G4, M4 | M2 | Minh gõ dở `đang gõ dở dòng này` trong khi Quan dán 10 dòng liên tiếp | 10 dòng hiện phía trên, chữ đang gõ còn nguyên, Enter gửi đúng | C | K3 |  |  |
| T-M07 | D4, D5 | M1 | Quan chat với Minh; Huy `/chat Quan` và gửi 2 tin; Quan `/chat Huy` | `New message from Huy (1 unread)`, `(2 unread)`, sau đó `Switched to Huy — 2 unread:` | B | K3 |  |  |
| T-M08 | F5, J1 | M2 | Quan `/leave`; Minh gõ text | Minh: `Quan left the chat`, rồi hint No active chat | A | K3 |  |  |
| T-M09 | E1–E4, F4, M3 | M2 | `make_testfile.py 50`; `/send test50.bin` trong khi hai bên vẫn chat | in 25/50/75/100%, toolbar chạy; chat không bị khựng; file trong `downloads/` có `sha256sum` khớp | C | K4 |  |  |
| T-M10 | J4 | M2 | (a) kill Minh khi đang nhận 40%; (b) kill Quan khi đang gửi | (a) Quan báo `failed at ~40%`; (b) Minh báo interrupted; không còn file `.part` nào | C | K5 |  |  |
| T-M11 | J3, E1 | M1 | `/send khongco.pdf`; `/send a.txt` khi chưa có partner | `File not found`; `No active chat` | C | K4 |  |  |
| T-M12 | J2 | M2 | kill -9 Minh rồi `/chat Minh` ngay (trong cửa sổ 10 s) | `Cannot connect to Minh: refused/timed out`, không crash | A | K5 |  |  |
| T-M13 | J5, F7 | M1 | `/foo`, `/status busy`, `/chat`, `/help` | gợi ý ngắn / usage / bảng lệnh | C | K2 |  |  |
| T-M14 | F8 | M2 | `/quit` khi đang có 2 kết nối và 1 transfer | các peer khác nhận BYE và offline ngay; không traceback; terminal trả về bình thường | A | K5 |  |  |
| T-M15 | D2, E3 | M2 | tin tiếng Việt có dấu, gõ bằng Unikey/EVKey; gửi `báo cáo.pdf` 2 lần | hiển thị đúng; lần 2 lưu thành `báo cáo (1).pdf` | C | K4 |  |  |
| T-M16 | N4 | M2 | Windows↔Windows và Windows↔macOS/Linux; tắt/bật quyền firewall | khi firewall chặn thì không thấy nhau (ghi vào issues_log); cho phép trên profile đang dùng thì chạy | B | K2 |  |  |
| T-M17 | A3, G3 | M1 | chạy `--plain` trong terminal của IDE | chạy được, output không trộn (dòng nhập có thể bị lẫn, chấp nhận được) | C | K4 |  |  |
| T-M18 | D06 | M1 | 2 instance cùng `--name Quan` | `/list` hiện `Quan#xxxx`; `/chat Quan` báo nhập nhằng | B | K3 |  |  |
| T-M19 | H1–H6 | M2 | `/threads` trong lúc đang chat với 2 người và gửi 1 file | thấy `udp-broadcaster`, `udp-listener`, `tcp-acceptor`, `recv-Minh`, `recv-Huy`, `file-send-1` | A | K4 |  |  |
| T-N01 | B1, I1 | N | máy không chạy lanchat: `nc -ul 9999` (Windows: `ncat -u -l 9999`) | thấy `HELLO\|Quan\|5000\|online\|...` mỗi 3 s | B | K2 |  |  |
| T-N02 | B3, M6 | N | `echo -n 'HELLO\|Fake\|5099\|online\|deadbeef' \| nc -u -b -w1 255.255.255.255 9999`; sau đó `echo hello \| nc -u -b ...` | Fake online rồi offline sau 10 s; gói rác bị bỏ, app không lỗi | B | K2 |  |  |
| T-N03 | M6, I2 | N | `echo garbage \| nc 192.168.1.10 5000` | app in `Protocol error ... connection closed`, vẫn chạy tiếp | A | K3 |  |  |
| T-N04 | I2, J2 | N | `nc -l 6000 \| xxd` + broadcast HELLO giả với port 6000; `/chat Fake` | xxd hiện `49 4e 54 52 00 00 00 3a {"v":1,...`; Fake không trả INTR nên báo `Cannot connect` sau 3 s | A | K3 |  |  |
| T-W01 | L3, B1, I1 | W | xem 5.4 | ảnh có gói HELLO, khoảng cách 3 s | B | K4 |  |  |
| T-W02 | L3, D1 | W | xem 5.4 | ảnh SYN/SYN-ACK/ACK kèm bảng seq/ack | B | K4 |  |  |
| T-W03 | I2, M5 | W | xem 5.4 | ảnh hex của frame MSG tiếng Việt | B | K5 |  |  |
| T-W04 | J1 | W | xem 5.4 | FIN khi `/leave`, RST khi kill | B | K5 |  |  |
| T-W05 | E4 | W | xem 5.4 | file đi trên một `tcp.stream` mới | B | K5 |  |  |
| T-W06 | D16 | W | xem 5.4 | gói UDP BYE khi `/quit` | B | K5 |  |  |
| T-R01 | A2, H7, M8 | R | grep import (chỉ `socket`, `threading`, `struct`, `json`, `hashlib`, `prompt_toolkit`, stdlib); không có `pickle`, `socketserver`, `asyncio`; kiểm quy tắc khóa ở 3.3; mỗi thread có try/except | checklist đạt hết | A (review chéo) | K5 |  |  |
| T-R02 | L1, L2, A1 | R | clone mới trên một máy sạch → làm theo README → `pytest -q`; đếm trang báo cáo; đối chiếu bảng phân công | chạy được trong ≤ 10 phút; báo cáo 5–10 trang | C | K5 |  |  |
| T-D01 | L4, M8 | M2 | tổng duyệt demo theo 5.3, bấm giờ | ≤ 10 phút, mọi bước đạt | Cả nhóm | K5 |  |  |

## 2. Bảng phủ ngược (Phần 5.2)


| YC | Test | YC | Test |
|---|---|---|---|
| A1 | T-R02 | F1 | T-U20, T-M02 |
| A2 | T-R01 | F2 | T-U19, T-U20, T-M05 |
| A3 | T-M06, T-M17 | F3 | T-U27, T-M05 |
| A4 | T-M01, T-M02 | F4 | T-M09 |
| A5 | T-I01, T-M05 | F5 | T-U28, T-M08 |
| A6 | T-M01 | F6 | T-M04 |
| B1 | T-N01, T-I08, T-W01 | F7 | T-U39, T-M13 |
| B2 | T-U11, T-U15, T-U18, T-M02 | F8 | T-I09, T-M14 |
| B3 | T-U16, T-M03, T-N02 | G1–G3 | T-M06, T-M17 |
| B4 | T-U15, T-U16, T-U21, T-M03 | G4 | T-U40, T-M06 |
| C1 | T-U39, T-M04 | H1–H6 | T-M19 |
| C2 | T-U17, T-M04 | H7 | T-U23, T-U40, T-R01 |
| D1 | T-I01, T-M05, T-W02 | I1 | T-U11–T-U14, T-N01, T-W01 |
| D2 | T-U01, T-U02, T-M15 | I2 | T-U01–T-U10, T-N03, T-N04, T-W03 |
| D3 | T-U24, T-M06 | I3 | T-U03–T-U06 |
| D4 | T-U25, T-U26, T-M07 | J1 | T-U05, T-U28, T-I05, T-M08, T-W04 |
| D5 | T-I02, T-M07 | J2 | T-I04, T-I10, T-M12, T-N04 |
| E1 | T-U32, T-U34, T-M09, T-M11 | J3 | T-M11 |
| E2 | T-U35, T-M09 | J4 | T-U33, T-U37, T-M10 |
| E3 | T-U30, T-U31, T-M15 | J5 | T-U27, T-U39, T-M13 |
| E4 | T-I07, T-M09, T-W05 | K1 | demo `tools/k1_*` (01/11) |
| K2 | T-M02–T-M04 (08/11) | K3 | T-M05–T-M08, T-I01–T-I06 (15/11) |
| K4 | T-M06, T-M09, T-I07 (22/11) | K5 | toàn bộ ma trận (29/11–06/12) |
| L1, L2 | T-R02 | L3 | T-W01, T-W02 |
| L4 | T-D01 | N1 | T-M01 |
| N2 | T-N01–T-N04 | N3 | T-I08, T-M01 |
| N4 | T-M16 | N5 | (tài liệu đọc, ghi vào TLTK) |

### Rubric → bằng chứng:**

| Rubric | Bằng chứng |
|---|---|
| M1 (15) | T-U11–T-U23, T-M02–T-M04, T-W01 |
| M2 (20) | T-I01–T-I03, T-M05–T-M08 |
| M3 (15) | T-U30–T-U37, T-M09, T-M10 |
| M4 (15) | T-U40, T-M06 |
| M5 (10) | T-U01–T-U10, T-W03, `docs/protocol.md` |
| M6 (10) | T-I04–T-I06, T-M10–T-M14, T-N02, T-N03 |
| M7 (10) | T-R02 |
| M8 (5) | T-D01, T-R01, pytest xanh |
