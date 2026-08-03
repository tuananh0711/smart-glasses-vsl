# AI runtime pipeline

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Điều phối normalization, window, inference và hậu xử lý.

## Phạm vi

Điều phối normalization, window, inference và hậu xử lý. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Pipeline không nhận ảnh trực tiếp vào GRU; chỉ landmark đã chuẩn hóa.

## Luồng hoạt động

FeatureFrame -> normalize -> ring buffer 60 -> TFLite -> confidence/debounce -> gloss.

## Ví dụ

Ngưỡng 0.85 và 5 frame trong PL2 là giá trị khởi đầu cần benchmark.

## Ghi chú triển khai

Không dùng YOLO làm mô hình chính.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [TFLITE_INFERENCE.md](TFLITE_INFERENCE.md)
- [SENTENCE_BUILDER.md](SENTENCE_BUILDER.md)