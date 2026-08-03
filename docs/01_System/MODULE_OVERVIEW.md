# Tổng quan module

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Danh mục module, trách nhiệm và trạng thái.

## Phạm vi

Danh mục module, trách nhiệm và trạng thái. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Pi: capture, mediapipe, normalize, inference, recognition, sentence, offline TTS/audio, api, logger, updater. Android: text presentation, connection, history, settings.

## Luồng hoạt động

Module lõi phát domain event; adapter hiển thị/mạng tiêu thụ event độc lập.

## Ví dụ

TTS/loa lỗi không được làm crash inference; network lỗi chỉ làm Android mất cập nhật và phát trạng thái disconnected.

## Ghi chú triển khai

Android skeleton là Implemented ở mức build config; mọi feature app và toàn bộ Pi là Planned.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)
- [../04_Android/ANDROID_ARCHITECTURE.md](../04_Android/ANDROID_ARCHITECTURE.md)
