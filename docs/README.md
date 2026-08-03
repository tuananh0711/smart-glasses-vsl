# Cổng tài liệu kỹ thuật

> Trạng thái: **Implemented**  
> Cập nhật: 2026-07-19

## Mục tiêu

Điểm vào bắt buộc cho người và AI Agent.

## Phạm vi

Điểm vào bắt buộc cho người và AI Agent. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Tài liệu được tổ chức theo dự án, hệ thống, Pi, AI, Android, API, kiểm thử, triển khai, agent và ADR.

## Luồng hoạt động

Đọc 00_Project trước, sau đó đọc miền sẽ sửa và ADR liên quan.

## Ví dụ

Agent sửa WebSocket phải đọc 05_API và 04_Android/DATA_FLOW.

## Ghi chú triển khai

PROJECT_BRIEF_DAY_DU.md và PL2 là nguồn chính thức; source quyết định trạng thái triển khai.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [00_Project/README.md](00_Project/README.md)
- [00_Project/CURRENT_STATE_ASSESSMENT.md](00_Project/CURRENT_STATE_ASSESSMENT.md)
- [99_Decisions/ADR-001.md](99_Decisions/ADR-001.md)
