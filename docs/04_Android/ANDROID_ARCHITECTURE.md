# Kiến trúc Android

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Ranh giới presentation/domain/data cho companion app.

## Phạm vi

Ranh giới presentation/domain/data cho companion app. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Single-activity Compose + Navigation; ViewModel/StateFlow; repositories bao REST/WebSocket/local persistence.

## Luồng hoạt động

UI intent -> ViewModel -> use case/repository -> Pi/local -> UiState.

## Ví dụ

RealtimeScreen không gọi OkHttp trực tiếp.

## Ghi chú triển khai

Không chứa MediaPipe/TFLite/AI inference.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md)
- [REPOSITORY_PATTERN.md](REPOSITORY_PATTERN.md)