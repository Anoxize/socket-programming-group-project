# Hướng dẫn dùng bộ khung (skeleton)

Bộ khung này dựng đúng cây thư mục và chữ ký hàm ở Phần 2 của tài liệu thiết kế. **Không có hàm nào chứa logic.**
Mỗi người tự viết thân hàm của mình, vì khi vấn đáp sẽ phải giải thích và sửa code trực tiếp.

## 1. Đọc khung thế nào

- **Docstring đầu mỗi file** cho biết: mục đích, owner, mã yêu cầu/rubric, được phép import module nào (Phần 3.1), và thread nào chạy code trong file (Phần 3.2).
- **Mỗi hàm** có: chữ ký cố định → docstring một dòng (tiếng Anh, giống tài liệu thiết kế) → mục **Gợi ý:** (cần làm gì, vì sao, test ID nào phải qua, bẫy cần tránh) → `raise NotImplementedError("TODO(<owner>): ...")`.
- Hằng số (`config.py`, `protocol.py`), dataclass, enum và exception đã khai báo sẵn vì chúng là **đặc tả**, không phải logic. Đừng đổi tên/kiểu nếu chưa báo nhóm.
- Tìm việc của mình: `grep -rn "TODO(A)" lanchat tools tests` (thay A bằng B hoặc C).

## 2. Ai sở hữu file nào

| Owner | Code | Test | Tài liệu |
|---|---|---|---|
| **A** (TCP core & tích hợp) | `lanchat.py`, `lanchat/__init__.py`, `protocol.py`, `connection.py`, `app.py`, `tools/k1_tcp_echo_*.py`, `tools/fake_peer.py`, `requirements*.txt`, `pytest.ini`, `.gitignore` | `test_protocol.py`, `test_connection_loopback.py` | `docs/design_decisions.md`, `docs/protocol.md`, biên tập báo cáo |
| **B** (Discovery, presence, chat) | `config.py`, `peer_registry.py`, `discovery.py`, `chat_manager.py`, `tools/k1_udp_test.py` | `test_udp_datagram.py`, `test_peer_registry.py`, `test_chat_manager.py`, `test_discovery_loopback.py` | `README.md`, `docs/wireshark/` |
| **C** (File, UI, QA) | `file_transfer.py`, `ui.py`, `commands.py`, `tools/make_testfile.py` | `conftest.py`, `test_file_transfer.py`, `test_commands.py`, `test_console.py` | `docs/test_report.md`, `docs/demo_script.md`, tổng hợp `docs/issues_log.md` |

Review chéo: B duyệt PR của A, C duyệt PR của B, A duyệt PR của C.

## 3. Thứ tự làm (theo Phần 8)

| Tuần | A | B | C | Mốc Chủ Nhật |
|---|---|---|---|---|
| T1 26/10–01/11 | `tools/k1_tcp_*`; bắt đầu `recv_exact`, `encode_frame` (viết T-U01, T-U03 trước) | `tools/k1_udp_test.py`; `config.py` xong | spike prompt_toolkit; `conftest.py`; nguyên mẫu `Console` | K1 + **đóng băng interface 01/11** |
| T2 02/11–08/11 | `protocol.py` xong (T-U01–T-U10); `app.py` tối thiểu | `peer_registry.py`, `discovery.py` (T-U11–T-U22) | `commands.py` (T-U38, T-U39), `ui.py` (T-U40) | K2: thấy nhau trên 2 máy |
| T3 09/11–15/11 | `ConnectionManager`, `fake_peer.py` (T-I01–T-I06, T-I10) | `chat_manager.py` (T-U23–T-U29), UDP BYE, T-I08 | `/chat`, `/leave`; helper file (T-U30–T-U32) | K3: chat 2 chiều, 3 peer |
| T4 16/11–22/11 | FILE → `on_file_socket`; `App.shutdown` (T-I07, T-I09) | Wireshark W1, W2; README v1 | `TransferManager`, `ProgressReporter` (T-U33–T-U37) | K4: file 50 MB khi đang chat |
| T5–T7 | gia cố lỗi, feature freeze 29/11, code freeze 02/12, nộp 09/12 | | | |

## 4. Quy trình git (Phần 7)

1. `main` được bảo vệ. Mỗi tính năng một nhánh: `git switch -c a/recv-exact`.
2. Commit nhỏ, thông điệp rõ (vd. `protocol: recv_exact loops until n bytes (T-U03)`).
3. Trước khi push: `pytest -q -m "not lan and not slow"` phải không có test **failed**.
4. Mở PR → người review chéo approve → merge. Không tự merge PR của mình.
5. Chữ ký hàm **đóng băng từ 01/11**. Muốn đổi: báo cả nhóm, sửa tài liệu thiết kế và `docs/protocol.md` trong cùng PR.
6. Gặp lỗi → ghi ngay vào `docs/issues_log.md`.

## 5. Chạy test và xem test "xanh dần"

```bash
pip install -r requirements-dev.txt
pytest -q                              # lúc đầu: toàn bộ là "s" (skipped), 0 failed, 0 error
pytest -q -rs                          # xem lý do skip: TODO(A)/TODO(B)/TODO(C)
pytest -q tests/test_protocol.py       # chạy riêng file của mình
pytest -q -m "not lan and not slow"    # bản nhanh trước mỗi lần push
```

Khi viết xong một hàm: mở test tương ứng (tên test ghi trong mục **Gợi ý**), xóa dòng `pytest.skip(...)`, viết thân test
theo docstring `T-Uxx — ... — Mong đợi: ...`, chạy lại. Test chuyển từ `s` sang `.` (passed) là xong. Fixture trong
`conftest.py` còn là stub thì test dùng nó vẫn bị skip, nên C cần viết `conftest.py` sớm (tuần 1).
Ghi số passed/skipped/failed của mỗi checkpoint vào `docs/test_report.md`.

## 6. Quy tắc bắt buộc

- **Không xóa docstring "Gợi ý:" cho đến khi viết xong hàm** (và test của hàm đó đã xanh). Khi xong, có thể thay phần Gợi ý bằng mô tả ngắn cách hàm làm việc.
- Không thêm import vi phạm Phần 3.1 (vd. `connection.py` import `file_transfer`). Người review kiểm điều này trong mỗi PR.
- Không I/O mạng và không `notify` khi đang giữ khóa dữ liệu; không giữ hai khóa cùng lúc; dùng `Lock`, không dùng `RLock` (Phần 3.3).
- Không dán code tìm được trên mạng mà mình không giải thích được: vấn đáp sẽ hỏi từng dòng.
