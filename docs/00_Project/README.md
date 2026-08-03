# Hướng dẫn dự án

> Trạng thái: **Implemented**  
> Cập nhật: 2026-07-19

## Mục tiêu

Quy tắc đọc, nguồn sự thật và trạng thái tài liệu.

## Phạm vi

Quy tắc đọc, nguồn sự thật và trạng thái tài liệu. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

SSOT: brief + PL2; implementation evidence: repository; ADR giải quyết mâu thuẫn.

## Luồng hoạt động

Brief -> PL2 -> source -> docs -> thay đổi -> kiểm thử -> cập nhật docs.

## Ví dụ

Nếu PL2 cũ nhắc YOLO nhưng brief chốt MediaPipe/GRU thì dùng quyết định Edge AI hiện hành.

## Ghi chú triển khai

Không ghi Implemented nếu không có bằng chứng trong source/config/test.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
- [REQUIREMENTS.md](REQUIREMENTS.md)
- [../99_Decisions/ADR-001.md](../99_Decisions/ADR-001.md)