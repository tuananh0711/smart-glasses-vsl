# Mô hình AI

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Đặc tả GRU sequence classifier và artifact.

## Phạm vi

Đặc tả GRU sequence classifier và artifact. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Input landmark sequence, GRU nhẹ, classifier khoảng 400 lớp có khả năng mở rộng; deploy TFLite.

## Luồng hoạt động

Train TensorFlow -> evaluate -> convert -> benchmark Pi -> publish ModelBundle.

## Ví dụ

Input dự kiến 60x144 theo PL2.

## Ghi chú triển khai

Số layer/hidden units, label map và metrics chưa tồn tại: Need Verification.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [DATASET.md](DATASET.md)
- [TRAINING.md](TRAINING.md)