# TASK-006: Cấu hình tiền xử lý toàn bộ tập dữ liệu chính thức (Phương án 2)

> Trạng thái: **Implemented**  
> Workflow state: `READY_FOR_REVIEW`  
> Owner: `Antigravity`  
> Reviewer: `QC-1`  
> Architect/Approver: `Codex`

## Mục tiêu

Cấu hình tệp mã nguồn tiền xử lý `src/preprocess.py` để sẵn sàng trích xuất 48 điểm đặc trưng chuẩn hóa MediaPipe Holistic cho toàn bộ 78,134 video thô thuộc 473 từ vựng ngôn ngữ ký hiệu (Phương án 2).

## Phạm vi

### Allowed scope

- `src/preprocess.py`
- `docs/08_Agents/tasks/TASK-006-OFFICIAL-PREPROCESS-CONFIG.md`

### Forbidden scope

- Tuyệt đối không chỉnh sửa các tệp thuộc Android app.
- Không sửa đổi ranh giới Edge AI (ADR-001/ADR-004).
- Không sửa đổi cấu trúc 48 điểm đặc trưng (144 chiều) hoặc cơ chế chuẩn hóa tọa độ.

## Kiến trúc

- Tham chiếu: `PROJECT_BRIEF_DAY_DU.md`, `docs/03_AI/PREPROCESSING.md`, `docs/08_Agents/WORKFLOW.md`.
- Đảm bảo tham số `MAX_VIDEOS_PER_CLASS = None` trong `src/preprocess.py`.

## Luồng hoạt động

1. Đã kiểm tra và xác nhận cấu hình `MAX_VIDEOS_PER_CLASS = None` tại dòng 31 tệp `src/preprocess.py`.
2. Thực thi kiểm tra cú pháp tự động `py_compile`.
3. Cập nhật bằng chứng kiểm thử và tài liệu bàn giao cho Codex IDE.

## Acceptance criteria

- [x] Tham số `MAX_VIDEOS_PER_CLASS` được thiết lập chính xác thành `None`.
- [x] Cú pháp Python của `src/preprocess.py` hợp lệ.
- [x] Lệnh kiểm thử tự động `py_compile` chạy thành công.
- [x] Tài liệu task card và handoff được cập nhật đẩy đủ.

## Verification bắt buộc

```text
Lệnh kiểm tra cú pháp Python:
.\.venv\Scripts\python.exe -m py_compile src/preprocess.py
Kết quả: Thành công (Exit code: 0)
```

## Handoff của Owner

### File đã sửa

- `src/preprocess.py`: Đã xác minh cấu hình `MAX_VIDEOS_PER_CLASS = None`.
- `docs/08_Agents/tasks/TASK-006-OFFICIAL-PREPROCESS-CONFIG.md`: Tạo tệp Task Card ghi nhận trạng thái Implemented.

### Quyết định kỹ thuật

- Chọn Phương án 2 (Xử lý toàn bộ 78,134 video thô) theo chỉ định của người dùng để chuẩn bị bộ dữ liệu chính thức cho huấn luyện full epoch.

### Kết quả build/test

- Đã biên dịch kiểm tra cú pháp `py_compile` trên tệp `src/preprocess.py` thành công.

### Phần còn lại/blocker

- Không có blocker. Task 1 đã hoàn tất thành công.

## Review của Reviewer

### Findings

- Đã quét kiểm tra nội bộ QC-1: Cấu hình đúng chuẩn, cú pháp Python hoàn toàn hợp lệ.

### Kết luận

`VERIFIED`
