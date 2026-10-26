# Quyết định thiết kế (D01–D26)

> Owner: Thành viên A. Phục vụ: M5, M7. Nguồn: Phần 1 của tài liệu thiết kế.
> Cột "GV?" đánh ✅ là quyết định **nên hỏi giảng viên** (buổi học thứ Tư 28/10/2026).
> Sau buổi hỏi: điền câu trả lời vào bảng thứ hai, rồi cập nhật cột "Quyết định" nếu GV yêu cầu đổi.
> Mọi thay đổi sau ngày đóng băng interface (01/11) phải báo cả nhóm và cập nhật lại `docs/protocol.md`.

## 1. Bảng quyết định

| # | Vấn đề mơ hồ (nguồn: Q4 / Gaps) | Quyết định | Lý do ngắn | GV? |
|---|---|---|---|---|
| D01 | Topology kết nối (Q4-1) | Mỗi cặp peer có **một kết nối TCP "chat" lâu dài**. Kết nối được mở *lười*: chỉ mở khi một bên gõ `/chat`. Khi đổi partner bằng `/chat X`, **các kết nối cũ vẫn giữ nguyên**. | Nhờ vậy tin nhắn từ người không phải partner hiện tại vẫn về được và được đếm unread (D4). Đây cũng là cách làm "multiple peers" (D5, M2). | |
| D02 | `/leave` làm gì (Gaps Q0) | `/leave` gửi frame `BYE {"reason":"leave"}`, đóng socket của partner hiện tại và bỏ chọn partner. Bên kia in `[*] Quan left the chat`. Nếu muốn nói tiếp thì gõ lại `/chat` để kết nối lại. | Khớp với chữ "close the current chat" trong đề. Trạng thái đơn giản. Wireshark thấy được FIN, dùng làm minh chứng. | ✅ |
| D03 | Hai bên `/chat` nhau cùng lúc (Q4-2) | Áp dụng tie-break tất định: **giữ kết nối do peer có `peer_id` nhỏ hơn khởi tạo**, đóng kết nối còn lại bằng `BYE {"reason":"duplicate"}`. Phía nhận BYE loại này không in gì. | Hai bên tự tính ra cùng một kết quả. Cách "giữ cái cũ" sẽ khiến cả hai kết nối đều bị đóng. | |
| D04 | Nhận diện người gọi trên socket vừa `accept()` (Q4-3) | Frame đầu tiên của kết nối chat bắt buộc là `INTR` (peer_id, name, tcp_port). Bên accept trả lại `INTR` của mình. Bên gọi kiểm tra peer_id có đúng người mình định gọi không. Nếu sau 5 s chưa có frame đầu thì đóng. | Port nguồn của bên gọi là ephemeral nên không dò ra danh tính được. Cách này vẫn chạy đúng khi nhiều instance chạy chung một máy. | |
| D05 | Khóa định danh peer (Q4-4) | `peer_id = uuid4().hex[:8]`, sinh mới mỗi lần chạy. peer_id là khóa của registry, connections, history và unread. `name` chỉ là nhãn hiển thị. **Lọc gói broadcast của chính mình theo peer_id**. | Lọc theo tên thì hai người trùng tên sẽ không thấy nhau. Lọc theo IP thì hỏng khi test nhiều instance trên một máy. | |
| D06 | Trùng tên (Q4-4) | Cho phép trùng. Khi trùng, hiển thị `Quan#3f9a` (4 ký tự hex đầu của peer_id). Nếu gõ `/chat Quan` mà có nhiều người tên Quan thì báo lỗi và yêu cầu dùng số hoặc `Quan#3f9a`. Tên hợp lệ: 1–20 ký tự, không chứa `\|`, không có ký tự điều khiển. | Mô hình P2P không có server nên không có ai đảm bảo tên duy nhất. | |
| D07 | Peer khởi động lại | Nếu xuất hiện HELLO có peer_id mới nhưng **cùng (ip, tcp_port)** với một entry cũ thì thay entry cũ, không để "ghost". | Tránh việc danh sách hiện 2 dòng cho cùng một người. | |
| D08 | Tính ổn định của `/chat <số>` (Q4-5) | Số thứ tự lấy theo **lần `/list` gần nhất** (danh sách peer_id lưu trong `CommandDispatcher`). Nếu chưa từng `/list` thì dùng snapshot hiện tại, sắp theo (name, peer_id). Nếu số đó trỏ tới peer đã offline thì báo lỗi. | Người dùng chọn đúng con số họ vừa nhìn thấy, kể cả khi danh sách đã thay đổi sau đó. | |
| D09 | Đơn vị độ dài (Q4-6) | Độ dài là **số byte của chuỗi UTF-8**. Chỉ decode khi đã nhận đủ frame. MSG tối đa 65 536 byte. Dòng dài hơn bị chặn ngay ở phía gửi. | `'Xin chào Việt Nam'` có 17 ký tự nhưng là 20 byte. Ghi nhầm số ký tự sẽ làm lệch stream. | |
| D10 | Cách phân khung (Q4-7) | **Header cố định 8 byte**: 4 byte ASCII là loại frame + 4 byte `uint32` big-endian là độ dài payload. Không dùng kiểu text `MSG\|len\|`. | Không phải dò dấu phân cách. An toàn với dữ liệu nhị phân. Tên file chứa `\|` vẫn được (vì tên nằm trong JSON). Loại frame vẫn đọc được bằng mắt trong Wireshark. Đề có ghi "create your protocol by yourself". | ✅ |
| D11 | Định dạng UDP | Dạng text: `HELLO\|name\|tcp_port\|status\|peer_id` và `BYE\|name\|tcp_port\|peer_id`. **Vẫn nhận** HELLO kiểu cũ 4 trường để tương thích với `udp_broadcast_demo.py`. IP lấy từ `addr[0]`, TCP port lấy từ trường trong gói. | Mở rộng tối thiểu so với ví dụ trong đề. Có thể dùng demo của thầy làm "peer giả" khi test. | |
| D12 | File đi chung hay tách kết nối (Q4-8) | **Mỗi lần gửi file mở một kết nối TCP riêng** tới listen port của peer. Frame đầu là `FILE`. | Chat không bị file lớn chặn (E4). Framing trên kết nối file rất đơn giản. Muốn hủy chỉ cần đóng socket. | ✅ |
| D13 | Hành vi phía nhận (Q4-9, Gaps) | **Tự động nhận**, không hỏi người dùng. Nhận được cả từ peer không phải partner hiện tại. Giới hạn 1 GiB. Phía nhận in một dòng lúc bắt đầu và một dòng kết quả. Phía gửi in tiến độ ở 25/50/75/100%. Bottom toolbar hiển thị % trực tiếp. | Hỏi accept/reject buộc thread nền phải gọi prompt, rất rắc rối với prompt_toolkit. | ✅ |
| D14 | Toàn vẹn dữ liệu và commit file (Q4-11) | Ghi vào `<final>.part`. Cả hai bên tính SHA-256 trong lúc truyền. Bên gửi gửi hash sau khi hết dữ liệu. Bên nhận so khớp rồi mới `os.replace(.part, final)`. Nếu sai hash hoặc bị gián đoạn thì đóng file, xóa `.part` và thông báo **cả hai phía**. | Đáp ứng J4. Thứ tự "đóng file rồi mới xóa" là bắt buộc trên Windows. | |
| D15 | Tên file trong `downloads/` (Q4-10) | `safe_filename`: bỏ phần thư mục theo cả `/` lẫn `\`, thay ký tự cấm, chặn tên dành riêng của Windows (`CON`, `NUL`…), tối đa 255 byte. Nếu trùng tên thì đổi thành `name (1).ext`. Tạo `.part` bằng chế độ `'xb'`. Mỗi instance có thư mục tải riêng qua `--downloads`. | Chống path traversal và tránh ghi đè file có sẵn. Nhiều instance trên một máy không giẫm lên nhau. | |
| D16 | Phát hiện offline (Q4-12) | Dựa vào timeout UDP 10 s (listener quét mỗi 1 s). Khi `/quit` gửi thêm **UDP BYE** để bên kia báo offline ngay. **Mất kết nối TCP không có nghĩa là offline**: chỉ đóng phiên chat và báo `Connection lost`. | Danh sách online chỉ lấy từ một nguồn là discovery. | |
| D17 | `/status` (Q4-13) | Đổi status thì **broadcast ngay** (đánh thức broadcaster), sau đó vẫn gửi định kỳ 3 s. Bên nhận in `[*] Minh is now away`. `away` chỉ là nhãn, tin nhắn vẫn tới bình thường. Khi gửi cho người đang away thì in thêm gợi ý `(Minh is away)`. | Demo thấy thay đổi ngay, không phải chờ đến chu kỳ 3 s. | |
| D18 | Địa chỉ broadcast (Q4-14) | Mặc định `255.255.255.255`. Có tùy chọn `--bcast` để dùng địa chỉ directed (vd. `192.168.1.255`, khi Windows có nhiều card mạng) hoặc `127.255.255.255` (một máy, không có mạng). | Theo gợi ý N3 trong đề. | |
| D19 | Phạm vi history (Q4-15) | Lưu trong RAM, mỗi peer tối đa 500 dòng. `/chat` chỉ phát lại tin **chưa đọc**, giống ví dụ trong đề. | Đơn giản. Nếu được yêu cầu sửa live, có thể thêm `/history n`. | |
| D20 | Gõ text khi chưa có partner (Q4-16) | In `[!] No active chat. Use /list then /chat <name\|number>`. Nếu partner rớt kết nối thì bỏ chọn partner và in thông báo. | Đáp ứng J5. | |
| D21 | Port (Q4-17) | TCP mặc định 5000, đổi bằng `--port`. Nếu port bận thì **báo lỗi rõ ràng rồi thoát**, không tự tăng port. UDP 9999 dùng chung cho mọi instance (SO_REUSEADDR, thêm SO_REUSEPORT nếu OS có). **Không bật SO_REUSEADDR cho socket TCP listen trên Windows.** | Kết quả tất định khi demo. Tránh lỗi "hijack port" trên Windows (bug #12). | |
| D22 | Console | prompt_toolkit `PromptSession` + `patch_stdout`. Mọi output đi qua `Console.notify()` có khóa. Có chế độ dự phòng `--plain` (dùng `input`/`print`) cho terminal trong IDE hoặc khi không phải TTY. | Đáp ứng G1–G4. Có đường lui nếu máy demo bị lỗi. | |
| D23 | Ngôn ngữ chuỗi in ra console | Tiếng Anh, giống các ví dụ trong đề (`[*] Connected to Minh (...)`). Báo cáo viết tiếng Việt. | Dễ đối chiếu từng dòng với đề. | ✅ (tùy nhóm) |
| D24 | Mô hình đồng thời | Dùng threads (H1–H6) với socket blocking. Acceptor và listener đặt `settimeout(1.0)` để định kỳ kiểm tra `stop_event`. Không dùng `select`. | Đúng thread model trong đề, dễ giải thích khi vấn đáp. | |
| D25 | Log | `--debug` ghi log ra `lanchat-<name>.log`, không in ra console. | Không làm vỡ dòng nhập. Có dữ liệu để viết mục "Khó khăn & giải pháp". | |
| D26 | Phát hiện peer mất tích trên kết nối chat | Đọc blocking, không đặt timeout. Phát hiện qua `sendall` lỗi hoặc qua discovery báo offline. Riêng socket truyền file đặt `settimeout(30)`. | Tránh hiểu nhầm "đang rảnh" thành "đã ngắt" (bẫy timeout đã nêu trong technical notes §1). | |

## 2. Câu trả lời của GV

| # | Câu hỏi | Câu trả lời của GV: | Ngày | Người ghi | Có đổi quyết định? |
|---|---|---|---|---|---|
| D02 | `/leave` làm gì (Gaps Q0) |  |  |  |  |
| D10 | Cách phân khung (Q4-7) |  |  |  |  |
| D12 | File đi chung hay tách kết nối (Q4-8) |  |  |  |  |
| D13 | Hành vi phía nhận (Q4-9, Gaps) |  |  |  |  |
| D23 | Ngôn ngữ chuỗi in ra console |  |  |  |  |

### Ba điều nữa cần hỏi giảng viên

| # | Câu hỏi | Câu trả lời của GV: | Ngày | Người ghi |
|---|---|---|---|---|
| Q1 | Trang bìa, mục lục và phụ lục có tính vào giới hạn 5–10 trang không? |  |  |  |
| Q2 | Lúc demo có được dùng hotspot điện thoại không (Wi-Fi trường có thể bật client isolation)? |  |  |  |
| Q3 | Xác nhận prompt_toolkit được dùng vì nó chỉ lo phần UI, còn networking vẫn dùng `socket` thuần (A2). |  |  |  |

## 3. Quyết định phát sinh trong lúc làm

<!-- TODO(A): mỗi quyết định mới thêm một dòng D27, D28… cùng định dạng bảng 1 (ví dụ: MSG chỉ có khoảng trắng có hợp lệ không?). -->

| # | Vấn đề | Quyết định | Lý do ngắn | Ngày | Người đề xuất |
|---|---|---|---|---|---|
|  |  |  |  |  |  |
