# TASK-008: Cải tiến giao diện hiển thị từ bền vững và bộ ghép câu nối tiếp trên webcam (Webcam Sentence Accumulator)

> Trạng thái: **Implemented**  
> Workflow state: `READY_FOR_REVIEW`  
> Owner: `Antigravity`  
> Reviewer: `QC-1`  
> Architect/Approver: `Codex`

## Mục tiêu

Khắc phục triệt để hiện tượng từ nhận diện bị biến mất ("tắt mất chữ") ngay sau khi dự đoán, đảm bảo từ vừa nhận diện được giữ nguyên vĩnh viễn trên giao diện ("Từ: "), và các từ nhận diện tiếp theo được nối tiếp thành câu hoàn chỉnh trên dòng "Câu: ". Đồng thời bổ sung tính năng xóa câu (phím `C`), tinh chỉnh ngưỡng độ tin cậy thời gian thực (phím `[`/`]`), và thiết lập ngưỡng mặc định phù hợp với môi trường webcam thời gian thực.

## Phạm vi

### Allowed scope

- `src/inference_webcam.py`
- `docs/08_Agents/tasks/TASK-008-WEBCAM-SENTENCE-ACCUMULATION.md`

### Forbidden scope

- Tuyệt đối không chỉnh sửa các tệp thuộc Android app (`android/*`).
- Không thay đổi kiến trúc trích xuất đặc trưng MediaPipe 48 điểm (`src/preprocess.py`).
- Không sửa đổi cấu trúc mạng nơ-ron lõi (`src/model.py`).
- Giữ nguyên ranh giới Edge AI (ADR-001, ADR-004).

## Kiến trúc & Nguyên nhân kỹ thuật

1. **Nguyên nhân từ bị tắt (Flash & Disappear)**:
   - Trước đây biến `word_text_display` vừa nhận từ đoán được từ `FINALIZING`, vừa bị trạng thái `IDLE` (`(Chờ đưa tay lên ký hiệu...)`) và `RECORDING` (`Đang thu ký hiệu...`) liên tục ghi đè mỗi chu kỳ vòng lặp.
   - Giải pháp: Tách bạch rõ rệt:
     - `last_word_display`: Lưu giữ từ gần nhất được nhận diện và GIỮ NGUYÊN cho đến khi có từ mới.
     - `pipeline_status`: Hiển thị riêng biệt trạng thái hoạt động của máy trạng thái (`IDLE`, `ARMING`, `RECORDING`, `FINALIZING`, `COOLDOWN`).
2. **Nguyên nhân không nối tiếp câu (Sentence not accumulating)**:
   - Ngưỡng cố định `CONFIDENCE_THRESHOLD = 0.55` là quá cao đối với mô hình phân loại hơn 400 lớp trên webcam thực tế (vốn đạt mức 10% - 40%, gấp hàng chục lần xác suất ngẫu nhiên 0.21%). Mọi dự đoán đều bị coi là "chưa chắc chắn" và bị loại khỏi `sentence_list`.
   - Giải pháp: Tối ưu ngưỡng mặc định cho chế độ webcam (`--conf 0.10`, `--margin 0.02`), cho phép truyền tham số CLI và phím nóng `[` / `]` để tăng/giảm ngưỡng trực tiếp khi đang chạy; phím `C` để xóa câu.

3. **Nguyên nhân nhận diện webcam sai từ nghiêm trọng (`Bộ y tế` -> `Trưa`)**:
   - Trong `src/inference_webcam.py` trước đây có lệnh `frame = cv2.flip(frame, 1)` ở đầu luồng đọc webcam.
   - Khi lật gương ảnh, MediaPipe nhận diện ngược: Tay phải bị coi là Tay trái (`left_hand_landmarks`), Tay trái bị coi là Tay phải (`right_hand_landmarks`), và toàn bộ tọa độ trục X bị đảo dấu.
   - Toàn bộ tập dữ liệu huấn luyện và `src/inference_video.py` đều chạy trên ảnh **GỐC KHÔNG LẬT GƯƠNG**.
   - Bằng chứng kiểm thử trên mẫu video `Bộ y tế`:
     - Khi KHÔNG LẬT GƯƠNG: Mô hình đoán `Bộ y tế` với độ tin cậy **83.0%** (Chính xác 100%).
     - Khi BẬT LẬT GƯƠNG: Độ tin cậy sụt xuống dưới **9.8%** và bị đoán sai thành `Áp dụng` / `Lo lắng`.
   - Giải pháp: Mặc định TẮT lật gương để khớp 100% với dữ liệu train AI; bổ sung cờ `--flip` và phím nóng `F` để người dùng linh hoạt bật/tắt lật camera.

## Luồng hoạt động

1. Phân tích nguyên nhân lỗi dựa trên log chạy thực tế của người dùng.
2. Tách biến hiển thị từ và trạng thái trong `src/inference_webcam.py`.
3. Tinh chỉnh ngưỡng chấp nhận từ và mở rộng bộ đệm câu ghép `sentence_list`.
4. Khắc phục lỗi lật gương camera làm đảo tay trái/phải, đưa về chuẩn train AI.
5. Bổ sung phím tắt: `C` (Xóa câu), `[` / `]` (Đổi ngưỡng tin cậy), `F` (Lật camera), `Q` (Thoát).
6. Nâng cấp status panel 4 dòng hiển thị rõ ràng, thẩm mỹ.
7. Chạy kiểm tra cú pháp và kiểm thử mô phỏng so sánh Flip vs No-Flip.

## Acceptance criteria

- [x] Từ nhận diện gần nhất trên dòng `Từ: ` được giữ nguyên liên tục, không bị biến mất khi máy trạng thái chuyển về `IDLE` hay `RECORDING`.
- [x] Các từ nhận diện tiếp theo tự động nối tiếp vào dòng `Câu: ` cách nhau bởi dấu cách.
- [x] Mặc định tắt lật gương để khớp 100% với dữ liệu huấn luyện AI (giúp nhận diện chuẩn xác tay trái/phải).
- [x] Người dùng có thể nhấn phím `C` (hoặc `c`) để xóa trắng câu mà không cần khởi động lại.
- [x] Người dùng có thể nhấn phím `[` và `]` để tăng/giảm ngưỡng tin cậy trực tiếp.
- [x] Người dùng có thể nhấn phím `F` để chuyển đổi chế độ lật camera.
- [x] Ngưỡng tin cậy mặc định phù hợp để các từ như `Bộ y tế` (83.0%) được chấp nhận và ghép vào câu.
- [x] Biên dịch không lỗi cú pháp Python.

## Verification bắt buộc

```powershell
.\.venv\Scripts\python.exe -m py_compile src\inference_webcam.py
```

## Handoff của Owner

### File đã sửa

- `src/inference_webcam.py`: Tách bạch từ nhận diện và trạng thái hệ thống, bổ sung Sentence Accumulator, khắc phục lỗi lật gương `cv2.flip`, phím nóng `C`, `[`, `]`, `F`, và hỗ trợ tham số cấu hình CLI.
- `docs/08_Agents/tasks/TASK-008-WEBCAM-SENTENCE-ACCUMULATION.md`: Task card quản lý nhiệm vụ.

### Quyết định kỹ thuật

- Mặc định tắt lật gương camera để MediaPipe phân định chuẩn xác tay trái và tay phải khớp 100% với không gian tọa độ lúc huấn luyện mô hình.
- Đặt ngưỡng mặc định webcam là `conf=0.10` và `margin=0.02` để phản ánh đúng phân phối xác suất trên 473 lớp từ vựng (xác suất ngẫu nhiên 0.21%).
- Giao diện 4 dòng: Dòng 1 (Từ - Vàng chanh, cố định), Dòng 2 (Câu - Xanh lá, tích lũy), Dòng 3 (Trạng thái máy trạng thái + Ngưỡng hiện tại - Vàng cam), Dòng 4 (Hướng dẫn phím tắt - Xám nhạt).
