# Wireshark: checklist chụp W1–W6

> Owner: Thành viên B. Phục vụ: L3 (báo cáo mục 7.3), M5. Nguồn: Phần 5.4 của tài liệu thiết kế.
> File capture đặt tên `W1_udp_broadcast.pcapng` … `W6_udp_bye.pcapng` ngay trong thư mục này;
> ảnh chụp đặt trong `screenshots/` theo tên `W1_*.png`, `W2_*.png`…

## Nguyên tắc chung

**Nguyên tắc chung:**
- Bắt trên **2 máy thật**, chọn giao diện Wi-Fi/Ethernet. Lưu file `.pcapng` vào `docs/wireshark/`.
- Nếu hai instance chạy trên cùng một máy Windows thì phải chọn adapter "Adapter for loopback traffic capture" (Npcap). Trên loopback không có header Ethernet nên filter `eth.dst` sẽ không khớp.
- Mỗi ảnh chụp cả 3 khung: Packet List, Packet Details, Bytes. Tô hoặc khoanh trường cần nói tới. Kèm 2–4 câu giải thích.

## Bảng checklist

| ID | Thao tác | Display filter | Chụp gì | Chú thích trong báo cáo |
|---|---|---|---|---|
| W1 | Chạy 2 peer, bắt 15 s | `udp.port == 9999` (thêm `&& ip.dst == 255.255.255.255`) | danh sách gói HELLO (cột Time cách nhau khoảng 3 s); Details: IP dst 255.255.255.255, MAC dst ff:ff:ff:ff:ff:ff, UDP 9999→9999, Length; Bytes: `HELLO\|Quan\|5000\|online\|...` | Broadcast tới mọi máy trong LAN. Không có ACK hay kết nối (connectionless). Liên hệ với DHCP Discover ở SL32 |
| W2 | Bắt capture rồi gõ `/chat Minh` | `tcp.port == 6000 && tcp.flags.syn == 1` (sau đó `tcp.stream eq N`) | 3 gói SYN → SYN,ACK → ACK; Details: flags, Seq/Ack tương đối | Bảng 9: No, Hướng, Flags, Seq, Ack, Len. Giải thích vì sao ack = seq+1 và vì sao seq hiển thị 0 (số tương đối). Dòng code gây ra: `create_connection` / `accept` |
| W3 | Gửi `Xin chào Việt Nam` | `tcp.stream eq N && tcp.len > 0` | gói PSH,ACK; Bytes tô 8 byte header `4d 53 47 20 00 00 00 14` và `c3 a0` | Minh chứng framing: 0x14 = 20 byte, không phải 17 ký tự |
| W4 | `/leave`; lần khác kill tiến trình | `tcp.flags.fin == 1 \|\| tcp.flags.reset == 1` | FIN,ACK hai chiều (khi leave) và RST (khi kill) | FIN là đóng êm, RST là bị hủy. Liên hệ J1 và `recv()` trả `b''` |
| W5 | `/send` trong lúc đang chat | `tcp.port == 6000` → Statistics › Conversations | 2 `tcp.stream` khác nhau: chat (port nguồn x) và file (port nguồn y); gói đầu có `FILE{...}` | Minh chứng D12/E4: file đi trên kết nối riêng |
| W6 | `/quit` | `udp contains "BYE"` | 1 gói `BYE\|Quan\|5000\|...` | Offline ngay, không phải chờ hết 10 s |

## Ô dán ảnh và chú thích

### W1

- [ ] Đã bắt `W1_udp_broadcast.pcapng` (máy / interface: ______ , ngày: ______)
- [ ] Đã chụp `screenshots/W1_udp_broadcast.png` (đủ 3 khung: Packet List, Packet Details, Bytes; đã tô trường cần nói)

<!-- TODO(B): ![W1](screenshots/W1_udp_broadcast.png) -->

Chú thích (2–4 câu):

> <!-- TODO(B) -->

### W2

- [ ] Đã bắt `W2_tcp_handshake.pcapng` (máy / interface: ______ , ngày: ______)
- [ ] Đã chụp `screenshots/W2_tcp_handshake.png` (đủ 3 khung: Packet List, Packet Details, Bytes; đã tô trường cần nói)

<!-- TODO(B): ![W2](screenshots/W2_tcp_handshake.png) -->

Chú thích (2–4 câu):

> <!-- TODO(B) -->

### W3

- [ ] Đã bắt `W3_msg_frame_hex.pcapng` (máy / interface: ______ , ngày: ______)
- [ ] Đã chụp `screenshots/W3_msg_frame_hex.png` (đủ 3 khung: Packet List, Packet Details, Bytes; đã tô trường cần nói)

<!-- TODO(B): ![W3](screenshots/W3_msg_frame_hex.png) -->

Chú thích (2–4 câu):

> <!-- TODO(B) -->

### W4

- [ ] Đã bắt `W4_fin_rst.pcapng` (máy / interface: ______ , ngày: ______)
- [ ] Đã chụp `screenshots/W4_fin_rst.png` (đủ 3 khung: Packet List, Packet Details, Bytes; đã tô trường cần nói)

<!-- TODO(B): ![W4](screenshots/W4_fin_rst.png) -->

Chú thích (2–4 câu):

> <!-- TODO(B) -->

### W5

- [ ] Đã bắt `W5_file_new_stream.pcapng` (máy / interface: ______ , ngày: ______)
- [ ] Đã chụp `screenshots/W5_file_new_stream.png` (đủ 3 khung: Packet List, Packet Details, Bytes; đã tô trường cần nói)

<!-- TODO(B): ![W5](screenshots/W5_file_new_stream.png) -->

Chú thích (2–4 câu):

> <!-- TODO(B) -->

### W6

- [ ] Đã bắt `W6_udp_bye.pcapng` (máy / interface: ______ , ngày: ______)
- [ ] Đã chụp `screenshots/W6_udp_bye.png` (đủ 3 khung: Packet List, Packet Details, Bytes; đã tô trường cần nói)

<!-- TODO(B): ![W6](screenshots/W6_udp_bye.png) -->

Chú thích (2–4 câu):

> <!-- TODO(B) -->

### Bảng 9 (cho W2): seq/ack của 3-way handshake

| No | Hướng | Flags | Seq | Ack | Len |
|---|---|---|---|---|---|
|  |  | SYN |  |  |  |
|  |  | SYN, ACK |  |  |  |
|  |  | ACK |  |  |  |
