# Test cases

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Kịch bản chức năng và lỗi trọng yếu.

## Phạm vi

Kịch bản chức năng và lỗi trọng yếu. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

TC-CAM, MP, MODEL, SENT, TTS/AUDIO, API, APP, UPDATE, OFFLINE.

## Luồng hoạt động

Arrange fixture/hardware -> act -> capture metrics/log -> assert -> attach evidence.

## Ví dụ

TC-OFFLINE-001: tắt router/phone; Pi vẫn tạo sentence và phát âm thanh qua loa.

## Ghi chú triển khai

PL2 có các mục boot <=60s, landmark, accuracy, TTS, Android, latency, soak, lighting; cần tái đo.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [TEST_PLAN.md](TEST_PLAN.md)
- [../00_Project/REQUIREMENTS.md](../00_Project/REQUIREMENTS.md)
