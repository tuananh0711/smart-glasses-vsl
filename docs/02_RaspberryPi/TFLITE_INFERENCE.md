# TFLite inference

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Contract nạp model và suy luận trên Pi.

## Phạm vi

Contract nạp model và suy luận trên Pi. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

ModelBundle gồm model.tflite, labels.json, metadata.json, checksum và compatibility version.

## Luồng hoạt động

Verify checksum/schema -> allocate interpreter -> warm-up -> infer -> map label.

## Ví dụ

Input dự kiến [1,60,144], output [1,num_classes].

## Ghi chú triển khai

INT8/FP16 là lựa chọn cần benchmark accuracy/latency, chưa được triển khai.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [../03_AI/MODEL.md](../03_AI/MODEL.md)
- [../07_Deployment/OTA_UPDATE.md](../07_Deployment/OTA_UPDATE.md)