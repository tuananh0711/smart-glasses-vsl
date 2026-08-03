# Kiểm thử hiệu năng

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Đo FPS, latency stage/end-to-end, CPU/RAM/nhiệt/power và soak.

## Phạm vi

Đo FPS, latency stage/end-to-end, CPU/RAM/nhiệt/power và soak. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Timestamp tại capture, landmark, inference, accepted gloss, sentence, bắt đầu phát âm thanh/API; báo p50/p95/p99.

## Luồng hoạt động

Warm-up -> fixed scenario -> 10+ phút -> collect -> analyze -> repeat.

## Ví dụ

Acceptance mục tiêu brief: 15-30 FPS và <300 ms; ghi rõ thiết bị/model/resolution.

## Ghi chú triển khai

Không suy diễn FPS từ camera FPS; cần end-to-end benchmark trên Pi 4.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [TEST_PLAN.md](TEST_PLAN.md)
- [../02_RaspberryPi/CAMERA_PIPELINE.md](../02_RaspberryPi/CAMERA_PIPELINE.md)
