# Huấn luyện

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Quy trình train/evaluate GRU có thể tái lập.

## Phạm vi

Quy trình train/evaluate GRU có thể tái lập. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Config-driven seed, split, augmentation, optimizer, checkpoints và reports.

## Luồng hoạt động

Validate data -> train -> early stop -> evaluate signer-independent -> export -> convert.

## Ví dụ

Báo cáo accuracy, macro F1, confusion matrix, size và Pi latency.

## Ghi chú triển khai

Mục tiêu test >=90% trong PL2 là tiêu chí dự kiến, chưa có bằng chứng.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [MODEL.md](MODEL.md)
- [MODEL_UPDATE.md](MODEL_UPDATE.md)