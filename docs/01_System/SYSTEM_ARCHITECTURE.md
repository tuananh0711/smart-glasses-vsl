# Kiến trúc hệ thống

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Kiến trúc logic và ranh giới phụ thuộc.

## Phạm vi

Kiến trúc logic và ranh giới phụ thuộc. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Camera -> Pi Edge Runtime -> offline TTS -> loa; API server là adapter tùy chọn để Android hiển thị văn bản. Android không nằm trên critical path.

## Luồng hoạt động

Capture queue -> landmark -> normalization -> 60x144 window -> TFLite -> smoothing -> sentence -> TTS/audio output và optional event bus.

## Ví dụ

Tắt hotspot chỉ làm app mất văn bản/telemetry; inference, Sentence Builder và âm thanh trên Pi vẫn hoạt động.

## Ghi chú triển khai

Hiện chưa có source Pi/API; sơ đồ là target architecture từ SSOT.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [DATA_FLOW.md](DATA_FLOW.md)
- [../99_Decisions/ADR-001.md](../99_Decisions/ADR-001.md)
