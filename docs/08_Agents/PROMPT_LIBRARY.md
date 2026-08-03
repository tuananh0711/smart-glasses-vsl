# Thư viện prompt

> Trạng thái: **Implemented**  
> Cập nhật: 2026-07-19

## Mục tiêu

Prompt chuẩn để onboard/review/implement.

## Phạm vi

Prompt chuẩn để onboard/review/implement. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Prompt luôn nhắc Edge AI, Pi autonomy, Android companion, evidence/status và tài liệu cần đọc.

## Luồng hoạt động

Chọn prompt -> gắn scope/files -> agent trả assumptions/evidence/tests/docs updates.

## Ví dụ

“Đọc docs/README.md và ADR trước; không đưa AI sang Android; đánh dấu Planned nếu thiếu source.”

## Ghi chú triển khai

Không nhúng bí mật hoặc dữ liệu cá nhân vào prompt/log.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [WORKFLOW.md](WORKFLOW.md)
- [CODEX.md](CODEX.md)