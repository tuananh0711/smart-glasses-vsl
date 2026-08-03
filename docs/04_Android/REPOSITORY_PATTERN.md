# Repository pattern

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Interface data access và error mapping.

## Phạm vi

Interface data access và error mapping. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

DeviceRepository, RealtimeRepository, HistoryRepository, SettingsRepository, ModelRepository.

## Luồng hoạt động

DTO -> mapper -> domain model; IOException/protocol errors -> typed AppError.

## Ví dụ

observeRecognition(): Flow<RecognitionEvent>.

## Ghi chú triển khai

Không để DTO/OkHttp Response đi vào Composable.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [ANDROID_ARCHITECTURE.md](ANDROID_ARCHITECTURE.md)
- [../05_API/ERROR_CODES.md](../05_API/ERROR_CODES.md)