# Luồng dữ liệu tổng thể

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Định nghĩa dữ liệu từ frame đến người dùng.

## Phạm vi

Định nghĩa dữ liệu từ frame đến người dùng. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Các stage dùng queue hữu hạn và timestamp đơn điệu để đo latency, tránh backlog.

## Luồng hoạt động

Frame -> 48x3 landmark -> normalized vector 144 -> window 60x144 -> probabilities -> accepted gloss -> sentence event.

## Ví dụ

Event có type=prediction, gloss, confidence, sentence, timestamp_ms.

## Ghi chú triển khai

Kích thước 48/144/60 theo PL2; cần xác minh khi code/model tồn tại.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [MODULE_OVERVIEW.md](MODULE_OVERVIEW.md)
- [../05_API/JSON_SCHEMA.md](../05_API/JSON_SCHEMA.md)