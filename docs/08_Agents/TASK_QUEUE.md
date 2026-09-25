# Hàng đợi nhiệm vụ đa Agent

> Trạng thái: **Planned** (Tài liệu kiến trúc đã có, mã nguồn Android chưa commit vào repo)  
> Cập nhật: 2026-09-23  
> Active task: `TASK-013-STATE-MACHINE-ACCURACY-RESTORE`

## Mục tiêu

Xác định thứ tự task để Codex có thể tạo và kích hoạt task tiếp theo một cách nhất quán sau khi task hiện tại hoàn thành.

File này đồng bộ **trạng thái công việc**, không tự khởi chạy ứng dụng hoặc mở chat mới cho agent.

## Phạm vi

Hàng đợi hiện bao phủ kế hoạch Android app-first. Mỗi task chỉ được kích hoạt sau khi task trước đã `DONE`, trừ khi Codex chứng minh hai task không sửa chung file và người dùng cho phép chạy song song.

## Kiến trúc

| Thứ tự | Task | Nội dung | Owner | Reviewer | Trạng thái |
|---:|---|---|---|---|---|
| 1 | TASK-001 | Android Phase 0 — Build foundation | Android Studio Agent | Antigravity | **Planned** (Docs ready, no source) |
| 2 | TASK-002 | App shell, navigation, design system | Android Studio Agent | Antigravity | **Planned** (Docs ready, no source) |
| 3 | TASK-003 | Realtime MVP bằng FakeRepository | Android Studio Agent | Antigravity | **Planned** (Docs ready, no source) |
| 4 | TASK-004 | JSON contract và WebSocket integration | Android Studio Agent | Antigravity | **Planned** (Docs ready, no source) |
| 5 | TASK-005 | History và local persistence | Android Studio Agent | Antigravity | **Planned** (Docs ready, no source) |
| 6 | TASK-006 | Device connection và Settings | Android Studio Agent | Antigravity | Queued |
| 7 | TASK-007 | Reverse Speech-to-Text | Android Studio Agent | Antigravity | Queued |
| 8 | TASK-008 | Debug, model update UI và hardening | Android Studio Agent | Antigravity | Queued |

## Luồng hoạt động

Khi active task chuyển `DONE`, Codex phải thực hiện trong cùng lượt nghiệm thu:

1. Đánh dấu task vừa xong là `Completed` trong bảng.
2. Chọn task `Queued` đầu tiên.
3. Tạo file task mới từ `TASK_TEMPLATE.md` nếu chưa tồn tại.
4. Điền Owner, Reviewer, scope, acceptance và verification.
5. Chuyển task mới thành `READY`.
6. Cập nhật `Active task` trong file này.
7. Cập nhật cả metadata và đường dẫn Current task trong `AGENT_START.md`.
8. Kiểm tra mọi liên kết.
9. Báo người dùng agent cần mở tiếp theo.

Android Studio Agent không tự tạo task kế tiếp sau khi code xong. Antigravity không tự tạo task kế tiếp sau khi review. Chỉ Codex/Approver thực hiện bước chuyển hàng đợi sau khi task đã `VERIFIED` và được nghiệm thu thành `DONE`.

## Ví dụ

Sau khi `TASK-001` đạt `DONE`, Codex tạo:

```text
docs/08_Agents/tasks/TASK-002-ANDROID-APP-SHELL.md
```

Sau đó cập nhật:

```text
AGENT_START.md Current task = TASK-002-ANDROID-APP-SHELL.md
TASK_QUEUE.md Active task = TASK-002-ANDROID-APP-SHELL
```

Trong chat mới, cả ba agent đọc `AGENT_START.md` và tự thấy task mới.

## Ghi chú triển khai

- Repository đồng bộ file, không đồng bộ bộ nhớ hội thoại của các agent.
- Agent chỉ thấy trạng thái mới sau khi được người dùng mở/gọi và yêu cầu đọc `AGENT_START.md`.
- Không bỏ qua review gate để “tự chạy liên tục” từ task này sang task khác.
- Không kích hoạt task tiếp theo nếu task hiện tại còn `CHANGES_REQUESTED`, `BLOCKED` hoặc thiếu verification.
- Nếu hai công cụ đang mở cùng file, bản ghi task trong repository được ưu tiên hơn nội dung chat cũ.

## Tài liệu liên quan

- [../../AGENT_START.md](../../AGENT_START.md)
- [WORKFLOW.md](WORKFLOW.md)
- [TASK_TEMPLATE.md](TASK_TEMPLATE.md)
- [tasks/TASK-001-ANDROID-PHASE-0.md](tasks/TASK-001-ANDROID-PHASE-0.md)
- [tasks/TASK-002-ANDROID-APP-SHELL.md](tasks/TASK-002-ANDROID-APP-SHELL.md)
- [tasks/TASK-003-ANDROID-REALTIME-FAKE.md](tasks/TASK-003-ANDROID-REALTIME-FAKE.md)
- [tasks/TASK-004-ANDROID-WEBSOCKET.md](tasks/TASK-004-ANDROID-WEBSOCKET.md)
- [tasks/TASK-005-ANDROID-HISTORY.md](tasks/TASK-005-ANDROID-HISTORY.md)
- [../04_Android/IMPLEMENTATION_PLAN.md](../04_Android/IMPLEMENTATION_PLAN.md)
