# Mã lỗi

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Taxonomy lỗi ổn định cho API/app/log.

## Phạm vi

Taxonomy lỗi ổn định cho API/app/log. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Nhóm SYS, CAM, MP, MODEL, API, CONFIG, UPDATE; response có code,message,retryable,details.

## Luồng hoạt động

Exception nội bộ -> typed domain error -> log -> sanitized API error.

## Ví dụ

MODEL_INCOMPATIBLE retryable=false; CAMERA_UNAVAILABLE retryable=true.

## Ghi chú triển khai

Không gửi stack trace hoặc đường dẫn nội bộ sang Android.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [REST_API.md](REST_API.md)
- [../06_Testing/TEST_CASES.md](../06_Testing/TEST_CASES.md)