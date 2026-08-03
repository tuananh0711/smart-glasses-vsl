# Điểm Khởi Động & Điều Phối AI Agent

> Trạng thái: **Implemented**  
> Cập nhật: 2026-07-22  
> Current task: `docs/08_Agents/tasks/TASK-005-ANDROID-HISTORY.md`

## Mục tiêu & Lệnh Khởi động

File này định hướng vai trò, thứ tự context và quy trình thực thi dành cho AI Agent trong kho mã `D:\do_an_tot_nghiep`.

Lệnh khởi động dành cho người dùng:

```text
Đọc D:\do_an_tot_nghiep\AGENT_START.md và tự thực hiện đúng vai trò đối với task hiện tại.
```

## Ràng buộc Kiến trúc Bất biến (Edge AI Boundaries)

1. **Raspberry Pi 4 B làm trung tâm Edge AI**: MediaPipe landmark extraction, normalization, GRU/TFLite model, và Sentence Builder chạy offline 100% trên Raspberry Pi (ADR-001).
2. **Kính không có màn hình (ADR-004)**: Kết quả nhận diện cử chỉ ghép thành câu được phát trực tiếp bằng offline Text-to-Speech (TTS) qua loa gắn trên kính.
3. **Android làm Companion App**: Ứng dụng Android kết nối REST/WebSocket để hiển thị phụ đề văn bản, xem lịch sử và quản lý cài đặt. Không đưa MediaPipe, TensorFlow hay TFLite mô hình dịch sang Android.
4. **Tính Hoạt động Độc lập**: Raspberry Pi phải hoàn toàn hoạt động bình thường khi mất kết nối điện thoại, Wi-Fi hoặc Internet.

## Thứ tự Đọc Nguồn Context

1. `AGENT_START.md` (Điểm khởi động chính)
2. `AGENTS.md` (hoặc `.agents/AGENTS.md` - Quy tắc bắt buộc & Handoff workflow)
3. `docs/README.md` (Cổng tài liệu kỹ thuật)
4. `docs/08_Agents/WORKFLOW.md` (Quy trình phối hợp)
5. `docs/08_Agents/TASK_QUEUE.md` (Hàng đợi task)
6. Current task file chỉ định (`docs/08_Agents/tasks/...`)
7. Tài liệu kỹ thuật liên quan trong `docs/`

## Quy trình Thực thi Task & Bàn giao (Agent Workflow)

1. **Nhận Task & Khoanh vùng Scope**:
   - Đọc kỹ thẻ Task hiện tại (`Allowed scope`, `Forbidden scope`, `Acceptance criteria`, `Verification commands`).
   - Chỉ chỉnh sửa các file thuộc `Allowed scope`.

2. **Lập trình & Kiểm thử Tự động (Verification)**:
   - Tiến hành lập trình/sửa đổi mã nguồn.
   - Bắt buộc thực thi lệnh kiểm thử tự động (ví dụ: `pytest`, `./gradlew assembleDebug test`) và xác nhận kết quả thành công.

3. **Kiểm thử Nội bộ (Internal QC-1)**:
   - Chạy subagent `QC-1` để đánh giá lại toàn bộ thay đổi.

4. **Nghiệm thu & Bàn giao Codex (External Codex Handoff)**:
   - Tạo file bàn giao `D:\do_an_tot_nghiep\agent_for_codex.md` tóm tắt thay đổi và danh sách file đã sửa.
   - Nhờ người dùng kích hoạt Codex IDE external chạy nghiệm thu cuối cùng và ghi kết quả vào `qc_report.md`.
   - Đọc `qc_report.md`: Nếu `PASS` $\rightarrow$ Task thành công, cập nhật trạng thái Task sang `DONE`.

## Quy ước Trạng thái

- **`Planned`**: Đã có thiết kế/tài liệu nhưng chưa có mã nguồn thực tế.
- **`Implemented`**: Đã có mã nguồn, chạy build/test thành công và verified.
- **`Need Verification`**: Có mã nguồn nhưng chưa đủ bằng chứng test tự động hoặc xác nhận phần cứng.
