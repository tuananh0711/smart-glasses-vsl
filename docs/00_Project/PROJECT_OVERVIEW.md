# Tổng quan dự án

> Trạng thái: **Implemented**  
> Cập nhật: 2026-07-19

## Mục tiêu

Mô tả sản phẩm kính thông minh dịch VSL sang tiếng Việt.

## Phạm vi

Mô tả sản phẩm kính thông minh dịch VSL sang tiếng Việt. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

OV5647 hướng về người ký; Pi 4 xử lý MediaPipe landmark, GRU/TFLite, Sentence Builder và phát kết quả bằng âm thanh qua loa. Android là companion tùy chọn để hiển thị văn bản.

## Luồng hoạt động

Người khiếm thính ký -> Pi nhận diện liên tục -> ghép câu -> Pi phát âm thanh qua loa; nếu có Android thì gửi văn bản để hiển thị.

## Ví dụ

Tôi + muốn + uống + nước -> “Tôi muốn uống nước.”

## Ghi chú triển khai

Mục tiêu khoảng 400 ký hiệu, mở rộng khoảng 1000; 15-30 FPS và <300 ms là mục tiêu brief, cần đo thực tế.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [REQUIREMENTS.md](REQUIREMENTS.md)
- [../01_System/SYSTEM_ARCHITECTURE.md](../01_System/SYSTEM_ARCHITECTURE.md)
