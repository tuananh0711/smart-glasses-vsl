# WebSocket

> Trạng thái: **Planned**  
> Cập nhật: 2026-07-19

## Mục tiêu

Kênh realtime Pi -> Android và command nhẹ.

## Phạm vi

Kênh realtime Pi -> Android và command nhẹ. Không mở rộng mục tiêu ngoài PROJECT_BRIEF_DAY_DU.md và PL2 - Anh - An.docx.

## Kiến trúc

/ws/v1/events; envelope version,event_id,type,timestamp_ms,payload; heartbeat/reconnect/idempotency.

## Luồng hoạt động

Handshake -> hello/capabilities -> subscribe -> event stream -> ping/pong -> reconnect.

## Ví dụ

type=sentence.updated payload chứa text và glosses.

## Ghi chú triển khai

Không dùng MQTT trừ khi có ADR mới; SSOT ưu tiên REST/WebSocket.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [JSON_SCHEMA.md](JSON_SCHEMA.md)
- [ERROR_CODES.md](ERROR_CODES.md)