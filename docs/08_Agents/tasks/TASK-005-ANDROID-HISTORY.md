# TASK-005: Android History và local persistence

> Trạng thái: **Planned**  
> Workflow state: `READY`  
> Owner: `Android Studio Agent`  
> Reviewer: `Antigravity`  
> Architect/Approver: `Codex`

## Mục tiêu

Lưu các câu hội thoại nhận được trên Android vào cơ sở dữ liệu cục bộ và thay màn hình Lịch sử placeholder bằng danh sách lịch sử có thể xem, tìm kiếm và xóa có kiểm soát.

## Phạm vi

### Allowed scope

- Android domain/data/history feature, navigation wiring và test liên quan.
- Room, SQLite schema, DAO, mapper và migration test.
- Gradle/version catalog cho Room/KSP và test dependency cần thiết.
- Documentation Android/Testing liên quan để ghi bằng chứng.

### Forbidden scope

- Không sửa Raspberry Pi/AI source hoặc WebSocket contract.
- Không triển khai Settings/discovery, Speech-to-Text, REST, OTA hoặc model update.
- Không thêm MQTT, Cloud AI, MediaPipe, TensorFlow hay TFLite vào Android.
- Không lưu raw video, ảnh camera hoặc dữ liệu sinh trắc học.
- Không làm persistence trở thành điều kiện để Pi hoạt động.

## Kiến trúc

```text
RealtimeRepository events
        -> HistoryRepository
        -> Room DAO
        -> Flow<List<ConversationEntry>>
        -> HistoryViewModel
        -> HistoryScreen
```

- `HistoryRepository` là interface domain-facing.
- DTO/Room entity không đi vào Composable.
- Database write chạy ngoài main thread.
- Chỉ lưu câu đã hoàn chỉnh và metadata tối thiểu: id, text, speaker, timestamp, source/status cần thiết.
- Có unique key/idempotency để reconnect không tạo bản ghi trùng.
- Schema version và migration phải rõ ràng; không dùng destructive migration trong production.

## Luồng hoạt động

1. Thiết kế domain model, Room entity, DAO và mapper.
2. Tạo `HistoryRepository` cùng implementation cục bộ.
3. Kết nối sentence event hoàn chỉnh từ realtime flow vào persistence mà không làm ViewModel phụ thuộc Room.
4. Triển khai `HistoryViewModel` bằng immutable `StateFlow`.
5. Thay placeholder bằng History screen: newest-first, empty/loading/error, tìm kiếm văn bản và xóa từng mục.
6. Thao tác xóa toàn bộ phải có confirmation; undo nếu phù hợp.
7. Thêm DAO/repository/ViewModel/UI test và migration test.
8. Chạy verification, ghi Handoff thực tế và chuyển `READY_FOR_REVIEW`.

## Acceptance criteria

- [ ] Room database, entity, DAO và mapper tách khỏi UI/domain model.
- [ ] `HistoryRepository` cung cấp Flow lịch sử và thao tác insert/delete/clear.
- [ ] Sentence hoàn chỉnh được lưu đúng một lần; duplicate event không tạo bản ghi trùng.
- [ ] History hiển thị newest-first với thời gian, speaker/source và nội dung rõ ràng.
- [ ] Có empty, loading và error state.
- [ ] Tìm kiếm lịch sử không phân biệt hoa thường và hoạt động ngoài Composable logic.
- [ ] Xóa từng mục hoạt động; xóa toàn bộ có confirmation.
- [ ] Không lưu video/ảnh hoặc dữ liệu ngoài phạm vi.
- [ ] Có DAO/repository/ViewModel tests và Room migration test.
- [ ] Build, unit test, lint và instrumentation test thành công.
- [ ] Không triển khai feature ngoài TASK-005.

## Verification bắt buộc

```text
gradlew.bat --stop
gradlew.bat clean assembleDebug
gradlew.bat testDebugUnitTest
gradlew.bat lintDebug
gradlew.bat connectedDebugAndroidTest
```

Owner phải ghi số test và kết quả report mới nhất; không dựa vào lời mô tả nếu XML report còn failure.

## Ví dụ

Khi nhận hai lần cùng `event_id=evt-42` cho câu “Tôi muốn uống nước.”, database chỉ có một bản ghi. Màn hình Lịch sử hiển thị bản ghi mới nhất trước và tìm kiếm `uống nước` phải tìm thấy câu này.

## Handoff của Owner

### File đã sửa

- Chưa triển khai.

### Quyết định kỹ thuật

- Chưa có.

### Kết quả build/test

- Chưa chạy.

### Phần còn lại/blocker

- Không có blocker ban đầu.

## Review của Reviewer

### Findings

- Chưa review.

### Kết luận

`PENDING`

## Ghi chú triển khai

Android Studio Agent là writer duy nhất khi task `IN_PROGRESS`. Antigravity chỉ review sau `READY_FOR_REVIEW`. Codex không sửa Android source. Room chỉ là lưu trữ companion app; Raspberry Pi không phụ thuộc database Android.

## Tài liệu liên quan

- [../WORKFLOW.md](../WORKFLOW.md)
- [../TASK_TEMPLATE.md](../TASK_TEMPLATE.md)
- [TASK-004-ANDROID-WEBSOCKET.md](TASK-004-ANDROID-WEBSOCKET.md)
- [../../04_Android/ANDROID_ARCHITECTURE.md](../../04_Android/ANDROID_ARCHITECTURE.md)
- [../../04_Android/DATA_FLOW.md](../../04_Android/DATA_FLOW.md)
- [../../04_Android/REPOSITORY_PATTERN.md](../../04_Android/REPOSITORY_PATTERN.md)
- [../../04_Android/SCREEN_SPECIFICATIONS.md](../../04_Android/SCREEN_SPECIFICATIONS.md)
- [../../06_Testing/TEST_PLAN.md](../../06_Testing/TEST_PLAN.md)
- [../../99_Decisions/ADR-001.md](../../99_Decisions/ADR-001.md)
- [../../99_Decisions/ADR-004.md](../../99_Decisions/ADR-004.md)
