# LAN Chat & File Sharing (Command-Line)

Đồ án CTT105 Mạng máy tính, Khoa CNTT, ĐH KHTN TP.HCM. Chat P2P và gửi file trong mạng LAN:
UDP broadcast để tìm nhau, TCP để chat và truyền file, giao diện dòng lệnh bằng prompt_toolkit.

> **Trạng thái:** đây đang là KHUNG (skeleton). Mọi hàm đều `raise NotImplementedError`.
> Đọc `HUONG_DAN_KHUNG.md` trước khi bắt đầu. Owner README: Thành viên B.

## 1. Giới thiệu và tính năng

<!-- TODO(B): 3–4 câu giới thiệu + danh sách tính năng đã chạy được thật (đánh dấu cái nào còn thiếu). Viết sau K3. -->

## 2. Yêu cầu

- Python ≥ 3.10
- Terminal thật: Windows Terminal / PowerShell / Terminal trên macOS/Linux. **Không** dùng IDLE.
  Terminal trong IDE có thể cần `--plain`.

<!-- TODO(B): ghi các OS nhóm đã thử thật và phiên bản Python. -->

## 3. Cài đặt

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate      macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt   # chỉ cần khi chạy test
```

<!-- TODO(B): kiểm lại từng lệnh trên máy sạch (T-R02). -->

## 4. Chạy trên 2 máy

```bash
python lanchat.py --name Quan
```

<!-- TODO(B): thêm ví dụ output 3 dòng khởi động (Phần 4.5) và ảnh chụp ngắn. -->

## 5. Chạy nhiều instance trên 1 máy

| OS | Lệnh |
|---|---|
| Linux | `python lanchat.py --name A --port 5001 --downloads dl_A --bcast 127.255.255.255` (tương tự cho B, C với port 5002, 5003) |
| Windows / macOS | dùng `--bcast 255.255.255.255`, hoặc địa chỉ directed như `192.168.1.255` |

<!-- TODO(B): ghi kết quả thử 127.255.255.255 trên Windows/macOS (rủi ro R4, tuần 1). Mỗi instance phải có port và thư mục downloads riêng. -->

## 6. Tùy chọn dòng lệnh

| Tùy chọn | Mặc định | Ý nghĩa |
|---|---|---|
| `--name NAME` | (bắt buộc) | Tên hiển thị, 1–20 ký tự, không chứa `\|`, không có ký tự điều khiển |
| `--port PORT` | `5000` | Cổng TCP listen cho chat và file. Bận thì báo lỗi và thoát mã 2 |
| `--udp-port PORT` | `9999` | Cổng UDP discovery, mọi peer dùng chung |
| `--bcast ADDR` | `255.255.255.255` | Địa chỉ broadcast (vd. `192.168.1.255`, hoặc `127.255.255.255` khi chạy một máy) |
| `--downloads DIR` | `downloads` | Thư mục lưu file nhận được |
| `--plain` | tắt | Dùng `input`/`print` thay cho prompt_toolkit (terminal IDE, không phải TTY) |
| `--debug` | tắt | Ghi log ra `lanchat-<name>.log` (không in ra console) |

## 7. Lệnh trong chương trình

| Lệnh | Ý nghĩa |
|---|---|
| `/list` | Liệt kê peer đang online, có đánh số (tên, IP, cổng TCP, trạng thái, số tin chưa đọc) |
| `/chat <tên\|số>` | Mở hoặc chuyển cuộc chat (vd. `/chat Minh`, `/chat 2`, `/chat Quan#3f9a`) |
| `/send <file>` | Gửi file cho người đang chat (cho phép dùng ngoặc kép khi tên có khoảng trắng) |
| `/leave` | Đóng cuộc chat hiện tại |
| `/status <online\|away>` | Đổi trạng thái của mình, bên kia thấy ngay |
| `/help` | In bảng lệnh |
| `/quit` | Thoát (Ctrl+D cũng thoát; Ctrl+C chỉ xóa dòng đang gõ) |
| `/threads` | (debug) Liệt kê các thread đang chạy |

Dòng không bắt đầu bằng `/` được gửi cho người đang chat.

## 8. Mạng và firewall

<!-- TODO(B): viết từ kinh nghiệm thật (issues_log.md):
     - Cho phép Python trên Windows Firewall, đúng profile (Private/Public).
     - Wi-Fi có client isolation (Wi-Fi trường) → dùng hotspot điện thoại.
     - Windows có nhiều card mạng → dùng --bcast x.x.x.255.
     - VPN / VirtualBox / WSL có thể "ăn" mất broadcast. -->

## 9. Kiểm thử

```bash
pytest -q -m "not lan and not slow"   # nhanh, chạy trước mỗi lần push
pytest -q                             # đầy đủ, chạy ở checkpoint
```

<!-- TODO(B): thêm các thao tác netcat (T-N01…T-N04 trong docs/test_report.md) và cách bắt Wireshark (docs/wireshark/README.md). -->

## 10. Cấu trúc thư mục và giao thức

<!-- TODO(B): cây thư mục rút gọn (một dòng mô tả cho mỗi file) + tóm tắt giao thức 5 dòng, trỏ tới docs/protocol.md. -->

## 11. Hạn chế đã biết và thành viên

<!-- TODO(B): hạn chế (không mã hóa, chỉ IPv4, history không lưu bền, broadcast không qua router…) và bảng thành viên (tên, MSSV, vai trò A/B/C). -->
