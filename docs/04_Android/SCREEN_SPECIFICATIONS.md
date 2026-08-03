# Đặc tả màn hình

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Hành vi và acceptance cho các màn hình companion.

## Phạm vi

Hành vi và acceptance cho các màn hình companion. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Realtime ưu tiên câu lớn + connection/latency; History; Reverse STT; Device/Settings; Debug; Model Update.

## Luồng hoạt động

WebSocket event -> state reducer -> sentence card/history; command cần feedback.

## Ví dụ

Mất kết nối giữ câu cuối và hiển thị timestamp stale.

## Ghi chú triển khai

STT trên Android là chức năng giao tiếp ngược tùy chọn, không thuộc AI dịch ký hiệu.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [NAVIGATION.md](NAVIGATION.md)
- [DATA_FLOW.md](DATA_FLOW.md)