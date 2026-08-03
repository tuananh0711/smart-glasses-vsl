# JSON Schema Contract (v1.0)

> Trạng thái: **Implemented** (Android Side)  
> Cập nhật: 2026-07-20

## Mục tiêu

Định nghĩa cấu trúc dữ liệu trao đổi giữa Raspberry Pi và Android App qua WebSocket, đảm bảo tính nhất quán, khả năng mở rộng và khử trùng lặp (deduplication).

## Kiến trúc Envelope

Mọi message gửi từ Pi đến Android đều phải tuân theo cấu trúc Envelope sau:

```json
{
  "version": "1.0",
  "event_id": "string (UUID hoặc monotonic counter)",
  "type": "string (loại sự kiện)",
  "timestamp_ms": "number (Epoch time)",
  "payload": "object (dữ liệu chi tiết)"
}
```

### Các loại sự kiện (type)

| Type | Ý nghĩa | Payload Fields |
| :--- | :--- | :--- |
| `sentence.updated` | Cập nhật câu nhận diện đầy đủ | `text`, `is_final` |
| `prediction.updated` | Cập nhật gloss đang dự đoán | `text` (gloss), `confidence` |
| `error` | Lỗi từ phía server (Pi) | `message`, `code` |
| `connection.state` | Trạng thái hệ thống (tùy chọn) | `status` |

## Chi tiết Payload

### 1. `sentence.updated`
Dùng khi mô hình AI đã hoàn thành nhận diện một câu hoặc cập nhật nội dung câu hiện tại.
```json
"payload": {
  "text": "Tôi muốn uống nước.",
  "is_final": true
}
```

### 2. `prediction.updated`
Dùng để hiển thị phản hồi tức thì (real-time feedback) cho người dùng về hành động (gloss) đang thực hiện.
```json
"payload": {
  "text": "uống",
  "confidence": 0.95
}
```

## Quy tắc triển khai

1.  **Deduplication**: Android sử dụng `event_id` để bỏ qua các message bị lặp lại trong vòng 200 message gần nhất.
2.  **Forward Compatibility**: Android bỏ qua các field lạ (`ignoreUnknownKeys = true`).
3.  **Error Handling**: Nếu `version` chính không khớp (ví dụ `2.x`), Android sẽ báo lỗi giao thức.

## Bằng chứng triển khai (Evidence)

-   **Source**: `app/src/main/java/com/example/smart_glass/data/network/dto/RecognitionEventDto.kt`
-   **Mapper**: `app/src/main/java/com/example/smart_glass/data/network/mapper/RecognitionMapper.kt`
-   **Test**: `app/src/test/java/com/example/smart_glass/data/repository/PiRealtimeRepositoryTest.kt`

## Tài liệu liên quan

- [WEBSOCKET.md](WEBSOCKET.md)
- [ERROR_CODES.md](ERROR_CODES.md)
