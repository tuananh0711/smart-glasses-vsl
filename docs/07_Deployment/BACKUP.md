# Sao lưu

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Bảo vệ config, model metadata, history và dataset cá nhân.

## Phạm vi

Bảo vệ config, model metadata, history và dataset cá nhân. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Local snapshots ưu tiên; cloud backup tùy chọn, mã hóa và không chứa video ngoài chính sách.

## Luồng hoạt động

Quiesce metadata -> snapshot -> checksum -> rotate -> restore test.

## Ví dụ

Restore config không được tự động activate model không tương thích.

## Ghi chú triển khai

Retention/quyền riêng tư cần xác minh với nhóm và người tham gia dữ liệu.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [DEPLOYMENT.md](DEPLOYMENT.md)
- [../99_Decisions/ADR-003.md](../99_Decisions/ADR-003.md)