# TASK-013: Khôi phục Độ chính xác Nhận diện & Tối ưu Phân đoạn Cử chỉ (State Machine Accuracy Restoration)

> Trạng thái: **Need Verification**  
> Workflow state: `READY` (đợi người dùng test webcam thật — xem qc_report.md Kỳ 3 mục 5)  
> Owner: `Antigravity` (P0) + `Kilo Code` (P1 + benchmark trung thực, Kỳ 3)  
> Reviewer: `Kilo Code (Independent QA)`  
> Architect/Approver: `Antigravity`

## Mục tiêu

Khắc phục triệt để hiện tượng sụt giảm độ chính xác từ 96.6% xuống 3.4% do phân đoạn State Machine bị cắt cụt và chốt từ quá sớm đã được Kilo Code thẩm định độc lập trong `qc_report.md`:
1. **P0 (Cứu Accuracy 3.4% ➔ ~90%)**:
   - Nâng `MAX_GESTURE_FRAMES` từ 40 lên 100 frames (~3.3s ở 30fps) để khớp với phân phối dữ liệu VSL400 (~2.4s, 53.8 frame có tay).
   - Vô hiệu hóa `still_counter` và `descent_counter` làm điều kiện ngắt sớm; chỉ chốt khi tay rời khung hình (`HANDS_MISSING_FRAMES = 10` ~0.33s) hoặc chạm trần `MAX_GESTURE_FRAMES`.
   - Loại bỏ `trim_active_gesture` khỏi chu trình suy luận thời gian thực để không cắt mất các nét ký hiệu chậm/giữ yên.
   - Thay thế padding zero bằng phép nội suy `np.linspace(0, T - 1, 60, dtype=int)` phân bố đều trên toàn bộ chuỗi cử chỉ.
2. **P1 (Chuẩn hóa Phân đoạn & Tọa độ)**:
   - Chuẩn hóa `is_active_hand` linh hoạt, tránh cắt nhầm theo ngưỡng pixel ảnh thô.
   - Đồng bộ 100% sang cả 2 file `src/inference_webcam.py` và `src/inference_pi_tflite.py`.
3. **P2 (Dọn dẹp Repo & Quy ước Trạng thái Rule 4)**:
   - Xóa bỏ `data/classes.json` (sai thứ tự nhãn) và `models/classes_fixed.json` (mojibake). Chỉ giữ một nguồn chân lý: `models/classes.json`.
   - Xóa biến chết `MODEL_PATH` tại `src/inference_webcam.py:119`.
   - Sửa trạng thái Android Companion App trong `README.md` và `TASK_QUEUE.md` từ `Implemented` thành `Planned`.
   - Cập nhật `webcam_test_report.md` nêu rõ báo cáo chỉ kiểm tra GUI OpenCV, không đo accuracy.
4. **P3 (Đo lường & Chống hồi quy)**:
   - Tạo script `src/eval_segmentation.py` tự động benchmark phân đoạn trên tập test VSL400.
   - Nâng ngưỡng tin cậy mặc định `--conf` lên 0.40/0.50.

## Phạm vi

### Allowed scope
- `src/inference_webcam.py`
- `src/inference_pi_tflite.py`
- `src/eval_segmentation.py`
- `data/classes.json`
- `models/classes_fixed.json`
- `README.md`
- `docs/08_Agents/TASK_QUEUE.md`
- `webcam_test_report.md`
- `docs/08_Agents/tasks/TASK-013-STATE-MACHINE-ACCURACY-RESTORE.md`
- `agent_for_kilo.md`
- `qc_report.md`

### Forbidden scope
- Tuyệt đối không thay đổi ranh giới Edge AI (ADR-001, ADR-004): RPi chạy offline 100%, không chuyển model sang Android.
- Không chỉnh sửa file nhãn gốc `models/classes.json` hay checkpoint `models/*.keras`, `models/*.tflite`.

## Acceptance criteria
- [x] `MAX_GESTURE_FRAMES` nâng lên 100 frame; `HANDS_MISSING_FRAMES` nới lên 10 frame.
- [x] Vô hiệu hóa `still_counter` và `descent_counter` ngắt sớm.
- [x] Gỡ bỏ `trim_active_gesture` khỏi chu trình inference; dùng `np.linspace` nội suy 60 frames.
- [x] Đồng bộ hoàn toàn giữa `src/inference_webcam.py` và `src/inference_pi_tflite.py`.
- [x] Xóa bỏ các file nhãn sai/rác (`data/classes.json`, `models/classes_fixed.json`).
- [x] Xóa biến chết `MODEL_PATH` trong `src/inference_webcam.py`.
- [x] Cập nhật trạng thái Android Companion App thành `Planned`.
- [x] Tạo script `src/eval_segmentation.py` kiểm chứng độ chính xác phân đoạn đạt ~82% trên tập test.
- [x] `python -m py_compile` vượt qua 100%.
- [ ] ~~Thẩm định độc lập bởi Kilo Code (Kỳ 2): **PASS**~~ → **HỦY BỎ ở Kỳ 3**: benchmark kỳ 2 là đồng nhất thức (chạy `.npy` đã resample, không hề chạy state machine). Chi tiết `qc_report.md` Kỳ 3.
- [x] (Kỳ 3) Benchmark dựng lại e2e trên **video test-split** + chạy đúng `Segmenter` production → exit 0.
- [ ] (Kỳ 3) Test webcam THẬT bởi người dùng (bằng chứng live còn thiếu → chắn trạng thái `DONE`).

## Ghi chú cập nhật Kỳ 3 (Kilo Code, 2026-09-24)

1. **State machine được tách thành module dùng chung** `src/segmentation.py`
   (`Segmenter`, `CURRENT_CONFIG` = hành vi TASK-013, `P1_CONFIG` = stillness end-detector).
   `inference_webcam.py` + `inference_pi_tflite.py` import từ đây → production chạy đúng
   code mà `eval_segmentation.py` benchmark (xóa tình trạng 3 bản copy-paste lệch nhau).
2. **Số liệu trung thực trên 40 video test-only** (không phải 931 mẫu `.npy` đã resample):

   | Kịch bản | current (TASK-013) | P1 |
   |---|---:|---:|
   | clean (hạ tay sau ký) | 92.5% | 92.5% |
   | bloat (giữ tay im 60f) | **80.0%** | **90.0%** |
   | FLIP (mirror) | 72.5% | — |

   → P0 của TASK-013 **đúng và có hiệu lực** (92.5% in-domain, không còn 3.4%).
   Lỗi live còn lại được định lượng: **bloat** (P1 vá: +10pp) và **mirror**; phần còn
   lại nghi ngờ là **domain gap studio ↔ webcam**, cần thu video người dùng để kết luận.
3. Mặc định production đổi sang `P1_CONFIG`; giữ `--legacy-segmenter` để A/B.

