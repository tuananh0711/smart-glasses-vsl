# Cấu trúc Android

> Trạng thái: **Implemented**  
> Cập nhật: 2026-07-19

## Mục tiêu

Package layout mục tiêu.

## Phạm vi

Package layout mục tiêu. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

app/{core,feature,realtime,history,settings,debug,connection,data,domain,designsystem}.

## Luồng hoạt động

Feature sở hữu UI/ViewModel; data sở hữu DTO/client; domain không phụ thuộc Android UI.

## Ví dụ

feature/realtime/RealtimeScreen.kt + RealtimeViewModel.kt.

## Ghi chú triển khai

Package feature-first nền tảng đã được triển khai với `core.designsystem`, `core.navigation`, `feature.realtime`, `feature.conversation`, `feature.history`, `feature.device` và `ui`. Namespace `com.example.smart_glass` vẫn cần quyết định tên production sau này.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [ANDROID_ARCHITECTURE.md](ANDROID_ARCHITECTURE.md)
- [CODING_STANDARD.md](CODING_STANDARD.md)
