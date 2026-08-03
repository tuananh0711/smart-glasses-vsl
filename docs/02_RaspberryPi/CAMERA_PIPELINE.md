# Camera pipeline

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Thu nhận OV5647 120 độ và tiền xử lý.

## Phạm vi

Thu nhận OV5647 120 độ và tiền xử lý. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Camera abstraction xuất frame RGB/BGR kèm id/timestamp; cấu hình 480p/720p.

## Luồng hoạt động

Open -> validate -> capture -> resize/colorspace -> enqueue newest -> metrics.

## Ví dụ

FramePacket(frame_id, captured_at_ns, image).

## Ghi chú triển khai

Camera nhìn người ký phía trước, không nhìn tay người đeo.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [MEDIAPIPE_PIPELINE.md](MEDIAPIPE_PIPELINE.md)
- [../06_Testing/PERFORMANCE_TEST.md](../06_Testing/PERFORMANCE_TEST.md)