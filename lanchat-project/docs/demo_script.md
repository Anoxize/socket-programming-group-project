# Kịch bản demo 10 phút

> Owner: Thành viên C. Phục vụ: L4, M8. Nguồn: Phần 5.5 của tài liệu thiết kế.
> Tổng duyệt: #1 thứ Năm 03/12, #2 thứ Bảy 05/12 (T-D01). Bấm giờ từng đoạn và ghi vào bảng cuối.

## Chuẩn bị (T−30 phút)

Checklist (đánh dấu `[x]` khi xong):

- [ ] 2 laptop nối chung hotspot điện thoại. Firewall đã cho phép `python` trên profile đang dùng.
- [ ] Laptop 1 mở 2 terminal: Quan `--port 5000` và Huy `--port 5001 --downloads dl_huy`. Laptop 2 mở 1 terminal: Minh `--port 6000`.
- [ ] Wireshark đã mở trên laptop 2. File `test50.bin` đã tạo sẵn và đã biết SHA của nó.
- [ ] Phóng to font terminal. Chuẩn bị sẵn ảnh dự phòng của W1/W2 và một video dự phòng.
- [ ] `pytest -q -m "not lan and not slow"` xanh trên cả 2 laptop (commit/tag: ______)
- [ ] Video dự phòng đã quay và mở sẵn

## Các bước

| Phút | Người thao tác | Bước | Điểm chứng minh | Xong? |
|---|---|---|---|---|
| 0:00–0:45 | A | Giới thiệu kiến trúc (Hình 1) và topology demo | A5 | [ ] |
| 0:45–2:00 | B | Khởi động lần lượt Quan, Minh, Huy → các dòng `[+] ... online`; `/list` trên cả 2 máy; Wireshark lọc `udp.port==9999` | M1, B1–B4 | [ ] |
| 2:00–2:45 | B | Minh `/status away`, bên kia thấy ngay; `/list`; `/status online` | C1, C2 | [ ] |
| 2:45–5:00 | A | Quan `/chat Minh` → Connected; chat 2 chiều có tiếng Việt. Minh gõ dở một dòng trong khi Quan dán 5 dòng → dòng gõ dở còn nguyên. Huy `/chat Quan` gửi 2 tin → Quan thấy `(2 unread)` → `/chat Huy` → `Switched — 2 unread` → `/chat 1` quay lại | M2, M4, D3–D5 | [ ] |
| 5:00–7:00 | C | Quan `/send test50.bin` → 25/50/75/100% và toolbar; trong lúc đó Minh và Quan vẫn chat. Done (SHA OK); trên laptop 2 chạy `sha256sum downloads/test50.bin` để so | M3, E1–E4 | [ ] |
| 7:00–8:30 | C | `/send khongco.pdf`; gõ `/foo`. Gửi file rồi kill Minh ở khoảng 40% → Quan báo lỗi; mở lại Minh, `downloads/` không có `.part`. `/chat Minh` khi Minh đang chết → báo lỗi, không crash; sau ≤ 10 s Minh offline | M6, J1–J5 | [ ] |
| 8:30–9:30 | B | Trên Wireshark: handshake (W2) và bytes của frame MSG (W3) | L3, M5 | [ ] |
| 9:30–10:00 | A | `/leave` và `/quit` → BYE, offline ngay; tóm tắt | F5, F8 | [ ] |

## Kết quả tổng duyệt

| Lần | Ngày | Tổng thời gian | Bước bị lỗi / chậm | Cách khắc phục | Người ghi |
|---|---|---|---|---|---|
| #1 | 03/12 |  |  |  |  |
| #2 | 05/12 |  |  |  |  |

## Phương án dự phòng

<!-- TODO(C): ghi rõ khi mạng hỏng thì chuyển sang gì (hotspot khác, chạy 3 instance trên 1 máy với --bcast, mở ảnh W1/W2, phát video). -->
