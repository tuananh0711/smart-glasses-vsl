# Hướng dẫn Antigravity

> Trạng thái: **Implemented**  
> Cập nhật: 2026-07-19

## Mục tiêu

Guardrail cho agent tự động hóa/IDE khác.

## Phạm vi

Guardrail cho agent tự động hóa/IDE khác. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Cùng source hierarchy và status taxonomy; mọi mutation phải có verification.

## Luồng hoạt động

Read -> plan -> change -> test -> document -> report evidence.

## Ví dụ

Không tạo mock rồi gắn trạng thái Implemented cho Pi production.

## Ghi chú triển khai

Tôn trọng companion-only boundary của Android.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [WORKFLOW.md](WORKFLOW.md)
- [../99_Decisions/ADR-001.md](../99_Decisions/ADR-001.md)