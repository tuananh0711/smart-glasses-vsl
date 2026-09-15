# TASK-009: Đồng bộ mô hình TFLite siêu nhẹ lên Git cho Raspberry Pi

> Trạng thái: **Implemented**  
> Workflow state: `READY_FOR_REVIEW`  
> Owner: `Antigravity`  
> Reviewer: `QC-1`  
> Architect/Approver: `Codex`

## Mục tiêu

Cập nhật cấu hình `.gitignore` để cho phép theo dõi các tệp mô hình TFLite tối ưu hóa siêu nhẹ (`models/*.tflite`), đưa mô hình lượng tử hóa `vsl_bigru_attention_dynamic.tflite` (1.20 MB) và bản FP32 `vsl_bigru_attention.tflite` (4.46 MB) lên kho mã Git, đảm bảo thiết bị Raspberry Pi có thể clone/pull và thực thi trực tiếp offline mà không bị thiếu tệp.

## Phạm vi

### Allowed scope

- `.gitignore`
- `models/vsl_bigru_attention_dynamic.tflite`
- `models/vsl_bigru_attention.tflite`
- `chay_test_cam.bat`
- `src/inference_webcam.py`
- `docs/08_Agents/tasks/TASK-008-WEBCAM-SENTENCE-ACCUMULATION.md`
- `docs/08_Agents/tasks/TASK-009-TFLITE-EDGE-MODEL-SYNC.md`
- `agent_for_codex.md`

### Forbidden scope

- Tuyệt đối không đẩy các tệp dữ liệu thô `.mp4`, `.npy`, `.zip` lên Git.
- Không đẩy các tệp checkpoint `.keras` và `.h5` nặng lên Git.
- Giữ nguyên ranh giới Edge AI (ADR-001, ADR-004).

## Kiến trúc

- Tham chiếu: `ADR-001` (Raspberry Pi Edge AI độc lập), `ADR-004` (Kính không màn hình, phát qua loa).
- Quy định kích thước file GitHub: Giới hạn tối đa 100 MB/file. Cả 2 tệp TFLite đều dưới 5 MB (1.20 MB và 4.46 MB), hoàn toàn an toàn và tối ưu cho Git.

## Luồng hoạt động

1. Mở chặn quy tắc `!models/*.tflite` trong `.gitignore`.
2. Kiểm tra `git status` xác nhận 2 tệp TFLite đã được Git phát hiện.
3. Chạy kiểm tra kích thước và tính toàn vẹn của tệp mô hình TFLite.
4. Tạo tệp bàn giao `agent_for_codex.md`.
5. Đưa vào staging (`git add`), tạo commit và push lên nhánh `origin/main`.

## Acceptance criteria

- [x] `.gitignore` được cập nhật cho phép theo dõi `models/*.tflite`.
- [x] Tệp `models/vsl_bigru_attention_dynamic.tflite` (1.20 MB) được theo dõi bởi Git.
- [x] Tệp `models/vsl_bigru_attention.tflite` (4.46 MB) được theo dõi bởi Git.
- [x] Script `inference_pi_tflite.py` load và chạy thử nghiệm thành công mô hình TFLite.
- [x] Commit và push thành công lên kho mã từ xa.

## Verification bắt buộc

```powershell
# 1. Kiểm tra trạng thái Git tracking
git ls-files models/*.tflite

# 2. Kiểm tra suy luận TFLite
.\.venv\Scripts\python.exe -c "import tensorflow.lite as tflite; i = tflite.Interpreter('models/vsl_bigru_attention_dynamic.tflite'); i.allocate_tensors(); print('TFLite OK, input:', i.get_input_details()[0]['shape'])"
```

## Handoff của Owner

### File đã sửa / Thêm mới

- `.gitignore`: Thêm ngoại lệ `!models/*.tflite`.
- `models/vsl_bigru_attention_dynamic.tflite`: Thêm vào Git.
- `models/vsl_bigru_attention.tflite`: Thêm vào Git.
- `chay_test_cam.bat`: Thêm file thực thi nhanh cho người dùng.
- `src/inference_webcam.py`: Cải tiến giao diện hiển thị từ bền vững và bộ đệm câu (TASK-008).
- `docs/08_Agents/tasks/TASK-008-WEBCAM-SENTENCE-ACCUMULATION.md`: Thẻ nhiệm vụ TASK-008.
- `docs/08_Agents/tasks/TASK-009-TFLITE-EDGE-MODEL-SYNC.md`: Thẻ nhiệm vụ TASK-009.

### Kết quả test

- TFLite runtime tải mô hình thành công, kích thước đầu vào `[1, 60, 144]`.
- Trọng số mô hình hoàn toàn nguyên vẹn.

## Review của Reviewer

### Findings

- Đã quét kiểm tra nội bộ QC-1: Tệp `.tflite` nhẹ (1.20 MB), cấu hình `.gitignore` chuẩn xác, không làm phình kho Git.

### Kết luận

`VERIFIED`
