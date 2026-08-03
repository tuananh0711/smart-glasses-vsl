# Design system

> Trạng thái: **Implemented**  
> Cập nhật: 2026-07-19

## Mục tiêu

Token màu, chữ, spacing, trạng thái và accessibility.

## Phạm vi

Token màu, chữ, spacing, trạng thái và accessibility. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Material 3 semantic tokens; trạng thái connected/degraded/disconnected không chỉ dùng màu.

## Luồng hoạt động

Theme -> components -> screen; hỗ trợ dark mode và font scaling.

## Ví dụ

ConnectionChip(icon,label,color) hiển thị “Mất kết nối”.

## Ghi chú triển khai

Design system nền tảng đã được triển khai trong `core.designsystem.theme`, gồm light/dark theme, typography phụ đề tiếng Việt và semantic status colors. Component sản phẩm chi tiết tiếp tục được mở rộng theo từng feature.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [SCREEN_SPECIFICATIONS.md](SCREEN_SPECIFICATIONS.md)
- [CODING_STANDARD.md](CODING_STANDARD.md)
