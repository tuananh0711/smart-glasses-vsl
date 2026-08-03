# Kiến trúc Raspberry Pi

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Thiết kế process/thread và failure isolation.

## Phạm vi

Thiết kế process/thread và failure isolation. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Ưu tiên một service có worker/queue hữu hạn; camera producer, AI consumer, TTS/audio, API và logger adapters.

## Luồng hoạt động

Newest-frame policy bỏ frame cũ khi AI chậm; watchdog báo lỗi và restart có kiểm soát.

## Ví dụ

Queue maxsize nhỏ ngăn latency tăng vô hạn.

## Ghi chú triển khai

PL2 đề xuất multithreading; chọn chi tiết concurrency sau benchmark.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [CAMERA_PIPELINE.md](CAMERA_PIPELINE.md)
- [AI_PIPELINE.md](AI_PIPELINE.md)
