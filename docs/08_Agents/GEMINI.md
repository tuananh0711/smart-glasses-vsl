# Hướng dẫn Gemini

> Trạng thái: **Implemented**  
> Cập nhật: 2026-07-19

## Mục tiêu

Guardrail cho Gemini Android Studio.

## Phạm vi

Guardrail cho Gemini Android Studio. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Đọc docs/README, 00_Project, 04_Android, 05_API và ADR trước sửa Android.

## Luồng hoạt động

Inspect source/status -> propose scoped change -> implement/test -> update docs.

## Ví dụ

Không thêm inference vào app dù tiện cho demo.

## Ghi chú triển khai

Nếu docs/source lệch, ghi Need Verification và tạo ADR thay vì tự đổi mục tiêu.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [WORKFLOW.md](WORKFLOW.md)
- [CODEX.md](CODEX.md)