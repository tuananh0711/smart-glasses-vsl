# Raspberry Pi subsystem

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Điểm vào cho runtime Edge AI.

## Phạm vi

Điểm vào cho runtime Edge AI. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

Python service đa stage; Pi là chủ sở hữu AI, Sentence Builder, offline TTS/loa và API.

## Luồng hoạt động

Boot -> self-check -> load model/config -> warm-up -> run pipelines -> graceful shutdown.

## Ví dụ

Không có Android, Pi vẫn nhận diện và phát kết quả qua loa; chỉ mất phần hiển thị văn bản.

## Ghi chú triển khai

Repository chưa có thư mục/source Pi.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [PI_ARCHITECTURE.md](PI_ARCHITECTURE.md)
- [../03_AI/MODEL.md](../03_AI/MODEL.md)
