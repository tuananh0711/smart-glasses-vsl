# Tiền xử lý AI

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Biến video thành tensor landmark tái lập.

## Phạm vi

Biến video thành tensor landmark tái lập. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Dùng cùng code normalization cho train và inference; gốc trung điểm vai, scale khoảng cách vai.

## Luồng hoạt động

Decode -> MediaPipe -> select 48 -> handle missing -> normalize -> window/pad -> save.

## Ví dụ

48x3=144 features/frame; 60 frames/window.

## Ghi chú triển khai

Cần version hóa preprocessing để tránh training-serving skew.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [DATASET.md](DATASET.md)
- [../02_RaspberryPi/MEDIAPIPE_PIPELINE.md](../02_RaspberryPi/MEDIAPIPE_PIPELINE.md)