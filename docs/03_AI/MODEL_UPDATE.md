# Cập nhật model

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Vòng đời model an toàn, rollback được.

## Phạm vi

Vòng đời model an toàn, rollback được. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Pi tải/import ModelBundle, xác minh chữ ký/checksum/compatibility, atomic switch và giữ phiên bản trước.

## Luồng hoạt động

Stage -> verify -> smoke test -> activate -> monitor -> rollback nếu lỗi.

## Ví dụ

Model v1.2 không activate nếu input_shape khác runtime contract.

## Ghi chú triển khai

Android chỉ ra lệnh/đẩy gói; Pi tự xác minh và sở hữu activation.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [../07_Deployment/OTA_UPDATE.md](../07_Deployment/OTA_UPDATE.md)
- [../05_API/REST_API.md](../05_API/REST_API.md)