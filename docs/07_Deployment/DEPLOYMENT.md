# Triển khai

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Provision Ubuntu Server/Pi runtime/app config.

## Phạm vi

Provision Ubuntu Server/Pi runtime/app config. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Versioned release, Python environment khóa version, systemd service, local config/secrets, healthcheck.

## Luồng hoạt động

Prepare OS -> install deps -> deploy bundle -> validate hardware -> smoke test -> enable service.

## Ví dụ

Service khởi động không cần Internet và không chờ Android.

## Ghi chú triển khai

Phiên bản Ubuntu/Python/MediaPipe cụ thể: Need Verification.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [OTA_UPDATE.md](OTA_UPDATE.md)
- [BACKUP.md](BACKUP.md)