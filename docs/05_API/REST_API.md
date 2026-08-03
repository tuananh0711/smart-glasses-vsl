# REST API

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Control/config/status/model endpoints trên mạng cục bộ.

## Phạm vi

Control/config/status/model endpoints trên mạng cục bộ. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

FastAPI adapter của Pi; versioned /api/v1; REST không nằm trên inference critical path.

## Luồng hoạt động

Request -> validate -> command service -> response/error; long operation trả operation_id.

## Ví dụ

GET /api/v1/health; GET /status; PUT /config; POST /models/stage.

## Ghi chú triển khai

Endpoint chính xác chưa có source server: Need Verification.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [WEBSOCKET.md](WEBSOCKET.md)
- [JSON_SCHEMA.md](JSON_SCHEMA.md)