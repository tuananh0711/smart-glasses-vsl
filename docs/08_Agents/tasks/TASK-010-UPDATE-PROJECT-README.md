# TASK-010: Cập nhật và Chuẩn hóa File README.md Đồ Án Kính Thông Minh VSL

> Trạng thái: **Implemented**  
> Workflow state: `READY_FOR_REVIEW`  
> Owner: `Antigravity`  
> Reviewer: `QC-1`  
> Architect/Approver: `Codex`

## Mục tiêu

Sửa lại toàn diện file `README.md` gốc của repository để phản ánh chính xác 100% thông tin đồ án tốt nghiệp:
1. Sửa lỗi sai thuật ngữ phần cứng nghiêm trọng ("Kính đeo tay" -> "Kính mắt thông minh Smart Glasses").
2. Làm rõ mô hình tương tác thực tế (Người nghe đeo kính, camera góc rộng hướng về người khiếm thính đối diện).
3. Khẳng định ranh giới kiến trúc Edge AI theo ADR-001 và ADR-004: 100% On-Device offline trên Raspberry Pi 4; Kính **KHÔNG CÓ MÀN HÌNH**; đầu ra chính là âm thanh phát qua **Loa tích hợp** (Offline TTS); ứng dụng **Android là Companion App** tùy chọn nhận dữ liệu hiển thị phụ đề qua WebSocket/REST API.
4. Cập nhật số lượng từ vựng chính xác (473 nhãn từ vựng trong `classes.json`).
5. Bổ sung kiến trúc mô hình học sâu nâng cấp (BiGRU + Multi-Head Self-Attention / GRU, TFLite Dynamic Range Quantization siêu nhẹ 1.20 MB).
6. Cập nhật đầy đủ cấu trúc thư mục code thực tế và hướng dẫn chạy kiểm thử chi tiết (cả chế độ PC Webcam và Raspberry Pi TFLite).

## Phạm vi

### Allowed scope
- `README.md`
- `docs/08_Agents/tasks/TASK-010-UPDATE-PROJECT-README.md`
- `agent_for_codex.md`

### Forbidden scope
- Tuyệt đối không tự động chạy lệnh push lên Git (theo yêu cầu rõ ràng từ người dùng).
- Không sửa đổi mã nguồn mô hình hoặc logic xử lý của hệ thống.
- Tuyệt đối tuân thủ ranh giới kiến trúc Edge AI (ADR-001, ADR-004).

## Tiêu chí Nghiệm thu (Acceptance Criteria)

- [x] Sửa triệt để lỗi "Kính đeo tay" thành "Kính mắt thông minh".
- [x] Trình bày rõ ràng luồng hoạt động: Người đeo kính hướng về phía người khiếm thính đứng đối diện.
- [x] Khẳng định kính không có màn hình (ADR-004), đầu ra chính là Loa phát giọng nói tiếng Việt bằng Offline TTS (`pyttsx3`).
- [x] Định vị rõ Android là Companion App kết nối Wi-Fi nội bộ qua WebSocket/REST API để hiển thị văn bản/lịch sử (ADR-001).
- [x] Cập nhật số lượng nhãn từ vựng chính xác: 473 từ vựng.
- [x] Cập nhật sơ đồ kiến trúc hệ thống, cấu trúc thư mục thực tế đầy đủ.
- [x] Hướng dẫn chạy thử nghiệm rõ ràng cho cả môi trường PC/Webcam (`inference_webcam.py` / `chay_test_cam.bat`) và môi trường Raspberry Pi (`inference_pi_tflite.py`).
- [x] Đầy đủ bảng trạng thái tính năng tuân thủ quy ước taxonomy (`Implemented`, `Planned`, `Need Verification`).
- [x] Chuẩn bị đầy đủ tài liệu bàn giao `agent_for_codex.md`.

## Lệnh Kiểm tra & Xác minh (Verification)

```powershell
# 1. Kiểm tra cú pháp Markdown và liên kết tệp
Get-Content -Path README.md -TotalCount 50

# 2. Kiểm tra tính nhất quán với ADR-001 và ADR-004
Select-String -Path README.md -Pattern "Kính đeo tay|màn hình trên kính"
```
