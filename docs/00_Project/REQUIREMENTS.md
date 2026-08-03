# Yêu cầu hệ thống

> Trạng thái: **Implemented**  
> Cập nhật: 2026-07-19

## Mục tiêu

Chuẩn hóa yêu cầu chức năng và phi chức năng từ SSOT.

## Phạm vi

Chuẩn hóa yêu cầu chức năng và phi chức năng từ SSOT. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

FR: capture, landmark, normalize, sequence inference, smoothing, sentence, TTS/loa trên thiết bị và optional API/app để hiển thị văn bản. NFR: offline-first, low latency, stable, retrainable, scalable.

## Luồng hoạt động

Mỗi yêu cầu đi qua Planned -> Implemented -> Verified khi có code và test evidence.

## Ví dụ

FR-CORE-01: mất Wi-Fi/Android, Pi vẫn nhận diện, ghép câu và phát kết quả bằng âm thanh qua loa. Không có yêu cầu màn hình trên kính.

## Ghi chú triển khai

Mục tiêu 15-30 FPS/<300 ms theo brief; PL2 nêu 10-18 FPS và <=1 s như giới hạn/kịch bản cũ, cần benchmark để chốt.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [ROADMAP.md](ROADMAP.md)
- [../06_Testing/TEST_PLAN.md](../06_Testing/TEST_PLAN.md)
