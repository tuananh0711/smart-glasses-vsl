# Sentence Builder

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Ghép gloss ổn định thành câu tiếng Việt.

## Phạm vi

Ghép gloss ổn định thành câu tiếng Việt. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

State machine nhận accepted gloss, loại lặp, phát hiện boundary và phát sentence event; hoạt động offline.

## Luồng hoạt động

Gloss -> debounce/deduplicate -> buffer -> boundary hạ tay/timeout -> format sentence.

## Ví dụ

[Tôi, muốn, uống, nước] -> “Tôi muốn uống nước.”

## Ghi chú triển khai

Ngữ pháp VSL khác tiếng Việt; phiên bản đầu rule-based phải được đánh giá, không tuyên bố dịch ngữ pháp đầy đủ.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [AI_PIPELINE.md](AI_PIPELINE.md)
- [../03_AI/MODEL.md](../03_AI/MODEL.md)