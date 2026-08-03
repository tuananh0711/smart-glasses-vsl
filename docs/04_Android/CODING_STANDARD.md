# Chuẩn code Android

> Trạng thái: **Implemented**  
> Cập nhật: 2026-07-19

## Mục tiêu

Quy ước cho code mới và review.

## Phạm vi

Quy ước cho code mới và review. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Kotlin official style, immutable state, structured concurrency, DI boundary, testable clock/dispatcher.

## Luồng hoạt động

Format/lint -> unit test -> instrumentation where needed -> docs/status update.

## Ví dụ

Không dùng GlobalScope; không hard-code Pi IP trong Composable.

## Ghi chú triển khai

Toolchain Phase 0 đã được xác minh với Kotlin 2.1.0, Compose Compiler Plugin 2.1.0, AGP 8.3.2 và Gradle 8.7 trong môi trường Java 21. Không tự nâng version trong feature task nếu không có lỗi hoặc task toolchain riêng.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
- [../06_Testing/TEST_PLAN.md](../06_Testing/TEST_PLAN.md)
