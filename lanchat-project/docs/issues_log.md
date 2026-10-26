# Nhật ký sự cố

> Owner: cả nhóm ghi, Thành viên C tổng hợp. Phục vụ: L2 (báo cáo chương 8 "Khó khăn và giải pháp").
> Quy tắc: gặp lỗi là ghi **ngay**, kể cả khi chưa sửa được. Chương 8 chỉ được viết từ những dòng có thật ở đây.
> Cột cuối ghi commit sửa lỗi (hash ngắn) và/hoặc ID test chứng minh đã hết lỗi (T-Uxx, T-Ixx, T-Mxx, ảnh Wxx).

| Ngày | Người ghi | Triệu chứng | Nguyên nhân | Cách sửa | Commit/Test ID |
|---|---|---|---|---|---|
| VÍ DỤ — 30/10/2026 | VÍ DỤ — B | VÍ DỤ — Máy Windows không thấy HELLO từ máy macOS dù cùng Wi-Fi; `nc -ul 9999` trên Windows cũng không nhận được gì | VÍ DỤ — Windows Firewall chặn Python trên profile "Public" (mạng Wi-Fi bị nhận là Public) | VÍ DỤ — Cho phép Python trên đúng profile; thêm hướng dẫn vào README mục 8 | VÍ DỤ — `a1b2c3d`, T-M16, T-N01 |
|  |  |  |  |  |  |

<!-- Xóa dòng VÍ DỤ khi đã có dòng thật đầu tiên. -->
