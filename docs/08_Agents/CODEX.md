# Hướng dẫn Codex

> Trạng thái: **Implemented**  
> Cập nhật: 2026-07-19

## Mục tiêu

Guardrail cho Codex trên toàn repository.

## Phạm vi

Guardrail cho Codex trên toàn repository. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

SSOT + evidence-first; giữ Edge AI boundary; không tuyên bố feature thiếu source.

## Luồng hoạt động

Read required docs -> inspect dirty state -> implement minimal scope -> verify -> update traceability.

## Ví dụ

Thay API schema phải cập nhật Pi, Android, tests và docs cùng change.

## Ghi chú triển khai

Không dùng Cloud AI cho inference.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [WORKFLOW.md](WORKFLOW.md)
- [PROMPT_LIBRARY.md](PROMPT_LIBRARY.md)