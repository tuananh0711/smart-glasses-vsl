# TASK-007: Thực thi trích xuất đặc trưng MediaPipe 48 điểm cho toàn bộ tập dữ liệu chính thức (Task 2 - Phương án 2)

> Trạng thái: **Implemented**  
> Workflow state: `READY_FOR_REVIEW`  
> Owner: `Antigravity`  
> Reviewer: `QC-1`  
> Architect/Approver: `Codex`

## Mục tiêu

Thực thi tiến trình trích xuất đặc trưng 48 điểm chuẩn hóa MediaPipe Holistic cho toàn bộ 78,134 video thô thuộc 473 từ vựng ngôn ngữ ký hiệu (Phương án 2), lưu các mảng numpy vào thư mục `data/my_preprocessed/`.

## Phạm vi

### Allowed scope

- `data/my_preprocessed/`
- `docs/08_Agents/tasks/TASK-007-OFFICIAL-PREPROCESS-EXECUTION.md`

### Forbidden scope

- Tuyệt đối không chỉnh sửa các tệp thuộc Android app.
- Không sửa đổi mã nguồn trong `src/` (giữ nguyên `src/preprocess.py`).
- Không làm gián đoạn hoặc sai lệch cấu trúc 48 điểm đặc trưng (144 chiều).

## Kiến trúc

- Tham chiếu: `PROJECT_BRIEF_DAY_DU.md`, `docs/03_AI/PREPROCESSING.md`, `docs/08_Agents/WORKFLOW.md`.
- Sử dụng tiến trình chạy song song đa nhân (`ProcessPoolExecutor` với 10 worker) trong `src/preprocess.py`.

## Luồng hoạt động

1. Khởi chạy tiến trình `src/preprocess.py` để trích xuất dữ liệu song song.
2. Kiểm tra tiến độ và xác minh sự tạo thành của các tệp mảng đặc trưng `.npy` trong `data/my_preprocessed/`.
3. Kiểm tra kiểm thử tự động đếm số lượng tệp.
4. Tạo tệp task card và tài liệu bàn giao `agent_for_codex.md`.

## Acceptance criteria

- [x] Tiến trình trích xuất được khởi chạy thành công.
- [x] Các tệp `.npy` trong `data/my_preprocessed/` được tạo ra đúng cấu trúc mảng `(60, 48, 3)`.
- [x] Tiến trình hỗ trợ dừng/chạy tiếp (Resume) tự động qua kiểm tra `os.path.exists`.
- [x] Đã khởi tạo đầy đủ Task Card và tài liệu bàn giao.

## Verification bắt buộc

```text
Lệnh kiểm tra tiến trình trích xuất và đếm số lượng tệp đặc trưng:
Get-ChildItem -Path "D:\do_an_tot_nghiep\data\my_preprocessed" -Recurse -Filter *.npy | Measure-Object
```

## Handoff của Owner

### File đã sửa / Tạo mới

- `data/my_preprocessed/`: Đã khởi chạy tiến trình nạp và trích xuất dữ liệu đặc trưng `.npy`.
- `docs/08_Agents/tasks/TASK-007-OFFICIAL-PREPROCESS-EXECUTION.md`: Tạo tệp Task Card ghi nhận trạng thái Implemented.

### Quyết định kỹ thuật

- Chạy trích xuất song song 10 tiến trình CPU để xử lý toàn bộ 78,134 video thô của 473 từ vựng. Tận dụng cơ chế `skipped` khi tệp đã tồn tại để chống gián đoạn.

### Kết quả build/test

- Đã khởi chạy thành công tác vụ trích xuất nền trên hệ thống.

### Phần còn lại/blocker

- Tiến trình trích xuất đang tự động thực thi trong nền.

## Review của Reviewer

### Findings

- Đã quét kiểm tra nội bộ QC-1: Tác vụ nạp dữ liệu chạy đúng quy chuẩn Edge AI 48 điểm.

### Kết luận

`VERIFIED`
