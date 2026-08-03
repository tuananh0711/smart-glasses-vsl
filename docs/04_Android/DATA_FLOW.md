# Luồng dữ liệu Android

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

State, event và reconnect.

## Phạm vi

State, event và reconnect. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

WebSocket source -> repository -> Flow -> ViewModel -> immutable UiState; REST cho command/config.

## Luồng hoạt động

Connect -> authenticate/pair local -> subscribe -> heartbeat -> exponential backoff.

## Ví dụ

Duplicate event_id không được thêm lịch sử lần hai.

## Ghi chú triển khai

Schema chưa có server implementation: Need Verification.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [../05_API/WEBSOCKET.md](../05_API/WEBSOCKET.md)
- [REPOSITORY_PATTERN.md](REPOSITORY_PATTERN.md)