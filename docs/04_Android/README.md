# Android companion app

> Trạng thái: **Implemented**  
> Cập nhật: 2026-07-19

## Mục tiêu

Điểm vào Android và trạng thái code.

## Phạm vi

Điểm vào Android và trạng thái code. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Target: Kotlin, Jetpack Compose, Material 3, repository pattern, REST/WebSocket; app chỉ presentation/control.

## Luồng hoạt động

Launch -> connect Pi hotspot -> subscribe events -> render -> cache history/config.

## Ví dụ

Disconnected UI không ảnh hưởng Pi.

## Ghi chú triển khai

Phase 0 đã được triển khai và review: Gradle foundation, launcher `MainActivity`, Material 3 Compose theme và test tối thiểu hoạt động. Navigation và các feature sản phẩm vẫn là **Planned**.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [ANDROID_ARCHITECTURE.md](ANDROID_ARCHITECTURE.md)
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
