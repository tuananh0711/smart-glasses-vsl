# HƯỚNG DẪN BÀN GIAO KIỂM THỬ KILO CODE (KỲ 3 — BENCHMARK TRUNG THỰC + P1)

> File này do Kilo Code (vai trò Reviewer) chuẩn bị cho chu kỳ đối soát tiếp theo
> theo **Quy tắc 1 — AGENTS.md**. Người dùng/Agent nội bộ xác nhận rồi chạy lại
> `kilo.exe run` để đối soát độc lập lần nữa nếu cần.

## 1. Danh sách file đã chỉnh sửa (kỳ 3, 2026-09-24)

| File | Thay đổi |
|---|---|
| `src/segmentation.py` | **MỚI**. Tách state machine + `extract_keypoints_48` + `is_active_hand` + `resample_gesture_linspace` thành module dùng chung. `Segmenter` + `CURRENT_CONFIG` (= hành vi TASK-013) + `P1_CONFIG` (stillness end-detector, `end_still_frames=14`, pre_roll 12, ARMING abort không xóa pre_roll). |
| `src/inference_webcam.py` | Bỏ state machine copy-paste → import `Segmenter`. Mặc định dùng `P1_CONFIG`, thêm `--legacy-segmenter` để A/B. Đồng bộ `--conf` mặc định = **0.40**. |
| `src/inference_pi_tflite.py` | Bỏ state machine + hàm trùng lặp → import `Segmenter`. Mặc định `P1_CONFIG`, tham số `legacy_segmenter`. `try...finally` flush cử chỉ đang dở. ADR-001/004 giữ nguyên. |
| `src/eval_segmentation.py` | **VIẾT LẠI**. Benchmark e2e chạy đúng `Segmenter` trên **video thuộc TEST-SPLIT** (không dùng train+test như trước → hết memorization). Kịch bản: whole-clip / current clean / current BLOAT / P1 clean / P1 BLOAT / FLIP. Tiêu chí PASS mới. |
| `qc_report.md` | Thêm **Kỳ 3**: hủy bỏ PASS Kỳ 2 (benchmark tautological), số liệu trung thực mới, việc còn tồn. |
| `docs/08_Agents/tasks/TASK-013-...md` | Hạ `Implemented/DONE` → **`Need Verification`** (Quy tắc 4) vì thiếu bằng chứng webcam thật. |

## 2. Tóm tắt nội dung & mục tiêu

Kỳ 2 đã "PASS" bằng một benchmark **không hề chạy state machine** (chỉ cắt
`.npy` đã resample sẵn 60 frame → kịch bản cap-100 ≡ chuẩn train). Số liệu
`82.49% / +31.15 điểm` là rỗng. Kỳ này:

1. **Dựng lại benchmark trung thực**: chạy đúng `Segmenter` production trên video
   **gốc, test-split-only**, MediaPipe frame-by-frame như webcam.
2. **Định lượng lỗi live còn lại**: trên 40 video test, current đạt **92.5% clean**
   nhưng rớt xuống **80.0% khi BLOAT** (người dùng giữ tay im sau khi ký — hành vi
   chuẩn của webcam, không có trong video studio). Mirror camera: **72.5%**.
3. **P1 vá bloat**: stillness end-detector (đo `end_still_frames=14 > max 10` frame
   đứng-yên giữa ký trên dữ liệu thật → không cắt nhầm) nâng bloat 80.0% → **90.0%**
   mà không hồi quy clean.
4. **Hạ trạng thái TASK-013** xuống `Need Verification` vì **thiếu bằng chứng từ
   webcam thật của người dùng** (nghi vấn domain gap studio↔webcam là trần thật).

## 3. Lệnh kiểm chứng (`.venv` Python — python toàn cục 3.13 lỗi protobuf)

```powershell
# (1) Cú pháp
.\.venv\Scripts\python.exe -m py_compile src/segmentation.py src/eval_segmentation.py src/inference_webcam.py src/inference_pi_tflite.py

# (2) Benchmark e2e trung thực — exit 0 = PASS
.\.venv\Scripts\python.exe -X utf8 src/eval_segmentation.py --videos 40 --hold 60
```

Số liệu kỳ vọng (đã đo): whole-clip 92.5% · current clean 92.5% · current bloat 80.0%
· P1 clean 92.5% · P1 bloat 90.0% · FLIP 72.5% → **PASS (exit 0)**.

## 4. Hướng dẫn cho Kilo Code / reviewer kỳ tới

- **Không tin QC-1/Kỳ 2**: chính nó đã cho PASS trên benchmark sai. Độc lập chạy lại
  lệnh (2) và tự đọc `eval_segmentation.py` để xác nhận nó chạy `Segmenter` trên
  **test-split**, không phải `.npy` đã resample.
- **Kiểm tra ADR (Quy tắc 2)**: `inference_pi_tflite.py` vẫn offline 100%, kính không
  màn hình (GUI mặc định TẮT), TTS worker thread, không đưa AI sang Android.
- **Ranh giới scope (Quy tắc 3)**: xác nhận `models/classes.json`, checkpoint `.keras`/
  `.tflite`, `data/classes.json`/`classes_fixed.json` (đã xóa) **không** bị đụng lại.
- **Edge case cần soi**: `Segmenter._drop_tail` khi gesture ngắn; `pending_gesture`
  flush khi thoát; `is_active_hand` khi pose không detect được; chuỗi < `min_gesture_frames`.
- **Việc CHƯA xong (chắn DONE)**: phải có **báo cáo accuracy trên webcam THẬT của người
  dùng** (mục 5 qc_report Kỳ 3). Nếu live vẫn thấp sau P1 → kết luận domain gap, cần
  thu video người dùng fine-tune, không phải tiếp tục chỉnh tham số.
- Ghi kết quả vào `qc_report.md`. PASS → ghi "PASS" kèm ngày; FAIL → nêu file/lỗi/cách sửa.
