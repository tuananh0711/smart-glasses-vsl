# OTA update

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Cập nhật runtime/model an toàn khi có mạng nhưng không phụ thuộc mạng để chạy.

## Phạm vi

Cập nhật runtime/model an toàn khi có mạng nhưng không phụ thuộc mạng để chạy. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Signed bundle, staging, compatibility check, atomic activation, health gate, rollback.

## Luồng hoạt động

Download/import -> checksum/signature -> stage -> smoke -> switch -> retain previous.

## Ví dụ

Mất mạng trong tải không ảnh hưởng phiên bản đang chạy.

## Ghi chú triển khai

Android có thể khởi tạo thao tác nhưng Pi quyết định activation.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [DEPLOYMENT.md](DEPLOYMENT.md)
- [../03_AI/MODEL_UPDATE.md](../03_AI/MODEL_UPDATE.md)