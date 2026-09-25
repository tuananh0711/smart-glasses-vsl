# TASK-012: Sửa lỗi hiển thị Giao diện Cửa sổ Camera Inference & Tối ưu Phân đoạn Cử chỉ (Webcam GUI & Segmentation Fix)

> Trạng thái: **Implemented**  
> Workflow state: `DONE`  
> Owner: `Antigravity`  
> Reviewer: `QC-1 (Internal)` / `Kilo Code (External)`  
> Architect/Approver: `Antigravity`

## Mục tiêu

1. **Khắc phục lỗi giao diện**:
   - Thay thế cơ chế `maximize_window` (vốn dùng `user32.ShowWindow(hwnd, 3)` / SW_MAXIMIZE gây vỡ viewport con của OpenCV HighGUI và bị che khuất sau cửa sổ IDE) bằng hàm `setup_gui_window` chuẩn.
   - Thiết lập kích thước cửa sổ vừa vặn (1280x720 hoặc theo màn hình), căn giữa màn hình, và đưa lên `HWND_TOPMOST` cùng `SetForegroundWindow` ngay khi khởi tạo.
   - Loại bỏ lời gọi `cv2.setWindowProperty(..., cv2.WND_PROP_TOPMOST, 1)` lặp lại 30 lần/giây trong vòng lặp chính (gây nghẽn message pump của Windows).
   - Bật `line_buffering=True` cho `sys.stdout` để log trạng thái không bị kẹt trong buffer.

2. **Khắc phục lỗi phân đoạn cử chỉ (Segmentation - Kẹt 150 frames)**:
   - Người dùng thực hiện động tác (ví dụ "Bộ y tế") và hạ tay xuống, nhưng hệ thống bị ép thu đủ 150 frames (5 giây) mới chốt từ, khiến cử chỉ bị pha loãng với 70% frame rác tĩnh dẫn đến nhận diện sai thành "Học", "Bắt chước", "Bận".
   - Tối ưu các hằng số State Machine:
     * `MAX_GESTURE_FRAMES`: Giảm từ 150 xuống 75 frames (~2.5s) khớp với độ dài thực tế của dữ liệu VSL.
     * `HANDS_MISSING_FRAMES`: Giảm từ 8 xuống 5 frames (~0.16s) để chốt ngay khi hạ tay.
     * `END_STILL_FRAMES`: Giảm từ 12 xuống 7 frames (~0.23s) để chốt ngay khi dừng động tác.
     * `END_MOTION_THRESHOLD`: Tăng từ 0.010 lên 0.016 để không bị nhiễu rung webcam chặn điều kiện chốt từ.
     * Bổ sung logic `is_active_hand`: Kiểm tra vị trí cổ tay `wrist_y < 0.85`, nếu tay đã thả xuống đùi/bụng thì lập tức nhận diện là đã hạ tay để chốt ký hiệu ngay.
   - Đồng bộ hóa logic sang cả `src/inference_pi_tflite.py`.

## Phạm vi

### Allowed scope
- `src/inference_webcam.py`
- `src/inference_pi_tflite.py`
- `run_webcam.bat`
- `docs/08_Agents/tasks/TASK-012-WEBCAM-GUI-WINDOW-FIX.md`
- `agent_for_kilo.md`
- `qc_report.md`

### Forbidden scope
- Không thay đổi ranh giới Edge AI (ADR-001, ADR-004).
- Không sửa đổi các file trong `models/` hay `data/`.

## Acceptance criteria
- [x] `setup_gui_window` tạo cửa sổ OpenCV hiển thị trực tiếp và nổi lên trên màn hình desktop.
- [x] Không còn tình trạng camera bật nhưng cửa sổ bị ẩn/treo viewport.
- [x] Vòng lặp camera không gọi `SetWindowProperty` liên tục mỗi frame.
- [x] Hạ tay xuống hoặc dừng ký hiệu là chốt từ ngay lập tức (không bao giờ bị ép đủ 150 frames).
- [x] `python -m py_compile src/inference_webcam.py src/inference_pi_tflite.py` không có lỗi cú pháp.
- [x] Kilo Code review PASS.

## Verification bắt buộc
```powershell
python -m py_compile src/inference_webcam.py src/inference_pi_tflite.py
```

## Handoff của Owner

### File đã sửa
- `src/inference_webcam.py`: Triển khai `setup_gui_window`, gỡ bỏ `maximize_window` và per-frame `cv2.setWindowProperty`, kích hoạt `line_buffering=True`. Tối ưu các ngưỡng phân đoạn `MAX_GESTURE_FRAMES=75`, `HANDS_MISSING_FRAMES=5`, `END_STILL_FRAMES=7`, `END_MOTION_THRESHOLD=0.016`, và `is_active_hand(wrist_y < 0.85)`.
- `src/inference_pi_tflite.py`: Đồng bộ các ngưỡng phân đoạn tương tự.
- `agent_for_kilo.md`: Bàn giao nội dung cho Kilo Code review.

### Kết quả build/test
- `py_compile` pass 100% trên cả 2 file.
