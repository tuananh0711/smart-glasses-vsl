# Kế hoạch kiểm thử

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Unit, integration, hardware-in-loop, performance, resilience và acceptance.

## Phạm vi

Unit, integration, hardware-in-loop, performance, resilience và acceptance. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Test pyramid cộng Pi benchmark; requirement traceability FR/NFR -> test id -> evidence.

## Luồng hoạt động

Build -> unit -> integration -> Pi/HIL -> end-to-end -> soak -> report.

## Ví dụ

Ngắt Wi-Fi giữa inference: kính vẫn dịch, app báo disconnected.

## Ghi chú triển khai

Test mẫu Android hiện có không kiểm tra chức năng dự án.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [TEST_CASES.md](TEST_CASES.md)
- [PERFORMANCE_TEST.md](PERFORMANCE_TEST.md)