# TASK-XXX: Tên nhiệm vụ

> Trạng thái: **Planned**  
> Workflow state: `READY`  
> Owner: `Chưa giao`  
> Reviewer: `Chưa giao`  
> Architect/Approver: `Codex`

## Mục tiêu

Mô tả một kết quả cụ thể có thể build, test và review. Không gộp nhiều phase không liên quan.

## Phạm vi

### Allowed scope

- Liệt kê thư mục/file Owner được sửa.

### Forbidden scope

- Liệt kê thư mục/file hoặc quyết định không được thay đổi.
- Không thay đổi Edge AI boundary.
- Không thêm MediaPipe/TensorFlow/TFLite/MQTT vào Android.

## Kiến trúc

Liệt kê tài liệu và ADR bắt buộc đọc, interface cần giữ và ranh giới dependency của task.

## Luồng hoạt động

1. Owner đọc task và docs.
2. Owner ghi thời điểm bắt đầu, chuyển `IN_PROGRESS`.
3. Owner triển khai và verification.
4. Owner ghi handoff, chuyển `READY_FOR_REVIEW`.
5. Reviewer ghi review và chuyển `VERIFIED` hoặc `CHANGES_REQUESTED`.
6. Codex nghiệm thu, cập nhật docs và chuyển `DONE`.

## Acceptance criteria

- [ ] Tiêu chí chức năng 1.
- [ ] Tiêu chí kiến trúc 2.
- [ ] Build thành công.
- [ ] Test thành công.
- [ ] Documentation/status được cập nhật.

## Verification bắt buộc

```text
Lệnh build:
Lệnh unit test:
Lệnh lint:
Lệnh UI/integration test nếu có:
```

## Ví dụ

`TASK-001` chỉ sửa toolchain, MainActivity và launcher manifest; không triển khai WebSocket hoặc History.

## Handoff của Owner

### File đã sửa

- Chưa có.

### Quyết định kỹ thuật

- Chưa có.

### Kết quả build/test

- Chưa chạy.

### Phần còn lại/blocker

- Chưa có.

## Review của Reviewer

### Findings

- Chưa review.

### Kết luận

`PENDING`

## Ghi chú triển khai

Chỉ Owner được sửa source khi workflow state là `IN_PROGRESS`. Reviewer không tự sửa trong lượt review đầu. Nếu đổi Owner, phải cập nhật file này trước khi agent mới bắt đầu.

## Tài liệu liên quan

- [WORKFLOW.md](WORKFLOW.md)
- [PROMPT_LIBRARY.md](PROMPT_LIBRARY.md)
- [../04_Android/IMPLEMENTATION_PLAN.md](../04_Android/IMPLEMENTATION_PLAN.md)
