# MediaPipe pipeline

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Trích xuất Hands + Pose/Holistic landmark.

## Phạm vi

Trích xuất Hands + Pose/Holistic landmark. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Chọn 42 điểm hai tay và 6 điểm thân trên theo PL2; missing landmark phải có mask/policy rõ.

## Luồng hoạt động

Frame -> detect/track -> select landmarks -> validate handedness -> FeatureFrame.

## Ví dụ

FeatureFrame.values có 48x3 trước flatten.

## Ghi chú triển khai

Face là khả năng mở rộng, không phải input bắt buộc hiện tại.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [AI_PIPELINE.md](AI_PIPELINE.md)
- [../03_AI/PREPROCESSING.md](../03_AI/PREPROCESSING.md)