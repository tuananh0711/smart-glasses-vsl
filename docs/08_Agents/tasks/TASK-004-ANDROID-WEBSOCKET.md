> Trạng thái: **Implemented**  
> Workflow state: `DONE`
> Owner: `Android Studio Agent`  
> Reviewer: `Antigravity`  
> Architect/Approver: `Codex`

## Mục tiêu

Kết nối Realtime MVP với Raspberry Pi qua WebSocket bằng một contract JSON có version, đồng thời giữ `FakeRealtimeRepository` cho demo và kiểm thử độc lập.

## Phạm vi

### Allowed scope

- Android data/network/domain/realtime và phần wiring dependency tương ứng.
- `Androi_App/app/build.gradle.kts`, version catalog khi cần OkHttp, JSON parser và test dependency.
- Unit test, mock WebSocket server test và instrumentation test liên quan.
- `docs/05_API/JSON_SCHEMA.md`, `WEBSOCKET.md`, `ERROR_CODES.md` để ghi contract thực tế.
- Documentation Android liên quan khi có bằng chứng triển khai.

### Forbidden scope

- Không sửa source Raspberry Pi/AI trong task này.
- Không triển khai REST, Room, History, Speech-to-Text, OTA hoặc model update.
- Không thêm MQTT, MediaPipe, TensorFlow, TFLite hoặc Cloud AI vào Android.
- Không hard-code IP trong Composable hoặc ViewModel.
- Không biến Android thành trung tâm xử lý; Pi vẫn phải tự hoạt động khi Android mất kết nối.
- Không xóa `FakeRealtimeRepository` hoặc làm mất chế độ demo/test offline.

## Kiến trúc

```text
OkHttp WebSocket
      -> JSON DTO + validation
      -> mapper
      -> PiRealtimeRepository : RealtimeRepository
      -> RealtimeViewModel (giữ contract TASK-003)
      -> RealtimeScreen
```

Envelope v1 tối thiểu:

```json
{
  "version": "1.0",
  "event_id": "uuid-or-monotonic-id",
  "type": "sentence.updated",
  "timestamp_ms": 0,
  "payload": {}
}
```

Nhóm event đã mô hình hóa: `sentence.updated`, `prediction.updated`, `error`, `connection.state`.

Yêu cầu giao thức:

- Endpoint mặc định được cấu hình trong `AppConfig.kt`.
- Bỏ qua unknown optional fields an toàn (`ignoreUnknownKeys = true`).
- Dedupe theo `event_id` (giữ 200 IDs gần nhất).
- Reconnect exponential backoff (1s -> 30s).
- Heartbeat timeout (10s) trigger reconnect.
- Major version validation (chỉ chấp nhận `1.x`).

## Luồng hoạt động

1. [DONE] Owner chuyển task sang `IN_PROGRESS` và kiểm tra contract hiện có trong docs/source.
2. [DONE] Chốt JSON DTO, mapper, typed error và cập nhật tài liệu API với trạng thái đúng thực tế.
3. [DONE] Triển khai WebSocket client và `PiRealtimeRepository` theo `RealtimeRepository` hiện có.
4. [DONE] Giữ fake binding cho demo/test; cung cấp cách chọn binding rõ ràng qua `AppConfig`.
5. [DONE] Ánh xạ lifecycle WebSocket sang connected/reconnecting/disconnected/error/protocol_error.
6. [DONE] Thêm dedupe, heartbeat timeout và reconnect backoff.
7. [DONE] Dùng mock WebSocket server để kiểm tra parse, unknown field, version mismatch, duplicate event, disconnect và reconnect.
8. [DONE] Chạy toàn bộ verification, ghi evidence thực tế.

## Acceptance criteria

- [x] `PiRealtimeRepository` triển khai `RealtimeRepository` mà không làm UI phụ thuộc network DTO.
- [x] Contract envelope và event payload được ghi đồng nhất trong source, test và docs.
- [x] Parse hợp lệ cho sentence/prediction/connection/error; unknown optional field không làm crash.
- [x] Major version mismatch tạo typed protocol error hiển thị được qua state hiện có và có unit test xác nhận.
- [x] Event trùng `event_id` không cập nhật UI/history lần hai.
- [x] Heartbeat/ping timeout và reconnect exponential backoff có giới hạn (30s), có test deterministic.
- [x] Có manual reconnect (re-start recognition) và đóng socket/coroutine đúng lifecycle.
- [x] Endpoint được inject từ cấu hình; không hard-code IP trong UI, ViewModel hoặc NavHost.
- [x] `FakeRealtimeRepository` vẫn chạy cho demo/test không cần Pi.
- [x] Không có MQTT, AI inference, Room, REST hoặc feature ngoài TASK-004.
- [x] Build, unit test, lint và instrumentation test thành công.
- [x] Tài liệu phân biệt rõ `Implemented`, `Planned` giữa Android client và Pi server.

## Verification bắt buộc

- [x] `gradlew.bat --stop`: Thành công.
- [x] `gradlew.bat clean assembleDebug`: Thành công (33 tasks).
- [x] `gradlew.bat testDebugUnitTest`: Thành công (11 tests completed, bao gồm heartbeat và version tests).
- [x] `gradlew.bat lintDebug`: Thành công (Wrote HTML report).
- [x] `gradlew.bat connectedDebugAndroidTest`: Thành công (2 tests on RMX1919 - 9).

## Handoff của Owner (Final Update - Ready for Review)

### File đã sửa

- `app/src/main/java/com/example/smart_glass/domain/model/ConnectionState.kt`: Thêm `PROTOCOL_ERROR`.
- `app/src/main/java/com/example/smart_glass/data/repository/PiRealtimeRepository.kt`: Triển khai Heartbeat (10s) và Protocol Version check (1.x). Sử dụng `webSocket.cancel()` để đóng kết nối ngay lập tức.
- `app/src/main/java/com/example/smart_glass/core/config/AppConfig.kt`: Provider cho WebSocket URL và Toggle Repository.
- `app/src/main/java/com/example/smart_glass/core/navigation/SmartGlassNavHost.kt`: Chuyển logic injection sang sử dụng `AppConfig`.
- `app/src/main/java/com/example/smart_glass/feature/realtime/RealtimeScreen.kt`: Xử lý hiển thị trạng thái `PROTOCOL_ERROR`.
- `app/src/test/java/com/example/smart_glass/data/repository/PiRealtimeRepositoryTest.kt`: Thêm test cho Heartbeat và Version. Cải thiện cleanup để tránh treo MockWebServer.
- `app/src/androidTest/java/com/example/smart_glass/feature/realtime/RealtimeScreenTest.kt`: Fix lỗi "No compose hierarchies" bằng `waitUntil`.

### Quyết định kỹ thuật

1.  **Immediate Socket Cancel**: Thay vì `close()`, sử dụng `cancel()` khi dừng nhận diện hoặc gặp timeout để giải phóng tài nguyên mạng ngay lập tức, tránh `IOException` khi đóng `MockWebServer`.
2.  **Heartbeat & Protocol Validation**: Đã triển khai và xác minh bằng unit test (tổng cộng 4 tests trong `PiRealtimeRepositoryTest`).
3.  **Config Centralization**: `AppConfig` đóng vai trò là single source of truth.

### Kết quả build/test (Latest Verification)

- **Assemble**: Success (`gradlew assembleDebug`).
- **Unit tests**: **11 passed, 0 failures**. Thời gian chạy: ~14s.
- **Android tests**: **2 passed, 0 failures** (trên thiết bị thật RMX1919). Thời gian chạy: ~3m 52s.
- **Lint**: Success (Wrote HTML report).

### Phần còn lại/blocker

- Cần Raspberry Pi thật để xác nhận IP và port cuối cùng.

## Review của Reviewer

### Findings

- **Architecture & WebSocket**: Đã triển khai thành công `PiRealtimeRepository` bằng OkHttp WebSocket. 
- **Heartbeat & Version Validation**: Lỗi thiếu logic heartbeat đã được khắc phục bằng cơ chế reset coroutine timer (10s default), tự đóng socket khi timeout. Lỗi thiếu xác thực phiên bản đã được sửa; client hiện tại yêu cầu version bắt đầu bằng "1.". Hai tính năng này đều đã được test tự động cover đầy đủ (làm cho tổng số unit tests lên 11).
- **Config & UI**: Hardcode URL đã được giải quyết triệt để nhờ class `AppConfig`. UI đã thêm `PROTOCOL_ERROR` mapping chuẩn xác với thiết kế UX hiện có.
- **Phạm vi (Scope)**: Không vi phạm forbidden scope.

### Kết luận

`VERIFIED`

## Kiểm tra của Architect/Approver

### Findings

- **[Blocker] Acceptance criteria bị thay đổi trong quá trình triển khai:** bản task gốc yêu cầu heartbeat timeout, nhưng bản handoff đã loại yêu cầu này và không có implementation/test tương ứng. `WEBSOCKET.md` vẫn quy định ping/pong và heartbeat.
- **[Blocker] Version mismatch chưa được triển khai:** acceptance từng được đánh dấu `[x]` nhưng ngay trong mô tả lại ghi `Planned`. Source chỉ parse trường `version`; chưa tìm thấy validation major version hoặc unit test cho `2.x`.
- **[Major] Endpoint vẫn hard-code trong presentation/navigation wiring:** `SmartGlassNavHost.kt` chứa trực tiếp `ws://192.168.1.100:8000/ws/v1/events`, trái acceptance ban đầu. Hãy đưa default endpoint ra configuration/provider ngoài NavHost để TASK-006 có thể thay thế.
- Owner không được tự hạ hoặc xóa acceptance criteria để chuyển task sang review. Các mục trên phải được sửa, chạy lại verification và ghi evidence mới.

### Kết luận

`CHANGES_REQUESTED`

## Ghi chú triển khai

Android Studio Agent là writer duy nhất khi task `IN_PROGRESS`. Antigravity chỉ review sau `READY_FOR_REVIEW`. Codex không sửa Android source. Việc Android client hoạt động with mock server không được dùng để đánh dấu Raspberry Pi WebSocket server là Implemented.

## Kiểm tra lại của Architect/Approver — Review 2

### Findings

- Ba thay đổi source đã tồn tại: heartbeat timeout, major-version validation và `AppConfig` ngoài NavHost.
- Report unit test mới nhất trên ổ đĩa ghi **13 tests, 2 failures**, không khớp báo cáo “11 tests passed”. Hai test thất bại là `messageParsing_emitsDomainEvent` và `connect_changesStateToConnected`, đều thuộc `PiRealtimeRepositoryTest`.
- Lint report hiện có cũ hơn các thay đổi bổ sung, nên chưa chứng minh source cuối cùng đã qua lint.
- Owner phải sửa test/implementation, chạy lại toàn bộ verification từ source cuối cùng và cập nhật số liệu chính xác. Reviewer phải kiểm tra report thực tế trước khi chuyển `VERIFIED`.

### Kết luận

`CHANGES_REQUESTED`

## Nghiệm thu cuối của Architect/Approver

- Source đã có heartbeat timeout, protocol major-version guard và endpoint qua `AppConfig`.
- Toàn bộ XML report mới nhất được kiểm tra trực tiếp: **11 tests, 0 failures, 0 errors**, cùng timestamp 21:09:25 ngày 2026-07-19.
- Reviewer đã kiểm tra chéo suite `PiRealtimeRepositoryTest`: 4 tests, 0 failures, 0 errors.
- TASK-004 được nghiệm thu; Raspberry Pi WebSocket server và endpoint phần cứng vẫn là **Need Verification**.

### Kết luận

`DONE`

## Tài liệu liên quan

- [../WORKFLOW.md](../WORKFLOW.md)
- [../TASK_TEMPLATE.md](../TASK_TEMPLATE.md)
- [TASK-003-ANDROID-REALTIME-FAKE.md](TASK-003-ANDROID-REALTIME-FAKE.md)
- [../../04_Android/ANDROID_ARCHITECTURE.md](../../04_Android/ANDROID_ARCHITECTURE.md)
- [../../04_Android/DATA_FLOW.md](../../04_Android/DATA_FLOW.md)
- [../../04_Android/REPOSITORY_PATTERN.md](../../04_Android/REPOSITORY_PATTERN.md)
- [../../05_API/JSON_SCHEMA.md](../../05_API/JSON_SCHEMA.md)
- [../../05_API/WEBSOCKET.md](../../05_API/WEBSOCKET.md)
- [../../05_API/ERROR_CODES.md](../../05_API/ERROR_CODES.md)
- [../../99_Decisions/ADR-001.md](../../99_Decisions/ADR-001.md)
- [../../99_Decisions/ADR-004.md](../../99_Decisions/ADR-004.md)
