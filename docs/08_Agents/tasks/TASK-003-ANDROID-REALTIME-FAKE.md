> Trạng thái: **Implemented**  
> Workflow state: `VERIFIED`  
> Owner: `Android Studio Agent`  
> Reviewer: `Antigravity`  
> Architect/Approver: `Codex`

## Mục tiêu

Biến màn hình `Phụ đề` từ placeholder thành Realtime MVP hoạt động hoàn toàn bằng dữ liệu giả lập, không cần Raspberry Pi hoặc network.

## Phạm vi

### Allowed scope

- `Androi_App/app/src/main/java/com/example/smart_glass/core/**`
- `Androi_App/app/src/main/java/com/example/smart_glass/data/**`
- `Androi_App/app/src/main/java/com/example/smart_glass/domain/**`
- `Androi_App/app/src/main/java/com/example/smart_glass/feature/realtime/**`
- `Androi_App/app/src/main/java/com/example/smart_glass/ui/**` khi cần wiring repository/ViewModel.
- `Androi_App/app/src/test/**`
- `Androi_App/app/src/androidTest/**`
- Gradle/version catalog chỉ khi cần dependency lifecycle/ViewModel/test đã được task cho phép.
- Documentation Android liên quan khi ghi evidence.

### Forbidden scope

- Không triển khai WebSocket, REST, Room hoặc persistence.
- Không hard-code IP Raspberry Pi.
- Không triển khai Speech-to-Text, model update, camera preview hoặc settings thật.
- Không thêm MediaPipe, TensorFlow, TFLite, Sentence Builder hoặc MQTT.
- Fake data không được mô tả như kết quả Pi thật.
- Không sửa Raspberry Pi/AI source, ADR hoặc API contract.

## Kiến trúc

Triển khai unidirectional data flow:

```text
FakeRealtimeRepository
        -> Flow<RecognitionEvent/ConnectionState>
        -> RealtimeViewModel
        -> StateFlow<RealtimeUiState>
        -> RealtimeScreen
```

Contract tối thiểu:

- `RealtimeRepository` interface.
- `FakeRealtimeRepository` deterministic, có start/stop hoặc coroutine lifecycle rõ.
- Domain model: `RecognitionEvent`, `Sentence`, `ConnectionState`, `Telemetry`, `DeviceEndpoint` nếu thực sự cần trong task.
- Immutable `RealtimeUiState`.
- `RealtimeViewModel` không phụ thuộc DTO/OkHttp/Android view.
- Dispatcher và clock có thể thay thế trong unit test.

## Luồng hoạt động

1. Owner chuyển task `IN_PROGRESS`, đọc source TASK-002 và tài liệu data/repository/screen.
2. Tạo domain model và repository interface.
3. Tạo fake fixture deterministic cho chuỗi `Tôi -> muốn -> uống -> nước`.
4. Tạo ViewModel/reducer state.
5. Xây Realtime Screen theo mockup đã phân tích: câu lớn, gloss mới, connection status, last-updated và 3–5 dòng gần nhất.
6. Hỗ trợ empty/loading/connected/reconnecting/disconnected/protocol-error UI state.
7. Khi disconnected, giữ câu cuối và đánh dấu stale; không tự phát fake event trong production binding.
8. Thêm unit test repository/ViewModel và Compose UI test phù hợp.
9. Chạy verification đầy đủ, ghi handoff và chuyển `READY_FOR_REVIEW`.

## Acceptance criteria

- [x] `RealtimeRepository` là interface độc lập UI/network.
- [x] `FakeRealtimeRepository` phát dữ liệu deterministic và hủy coroutine đúng lifecycle.
- [x] `RealtimeViewModel` dùng immutable `StateFlow<RealtimeUiState>`.
- [x] Demo tạo đúng câu “Tôi muốn uống nước.” mà không cần Pi/network.
- [x] UI hiển thị câu hoàn chỉnh cỡ lớn, gloss mới, trạng thái kết nối và thời điểm nhận cuối.
- [x] UI chỉ hiển thị tối đa 3–5 hội thoại gần nhất ở màn hình chính.
- [x] Có loading, empty, connected, reconnecting, disconnected và error state.
- [x] Disconnected giữ câu cuối nhưng thể hiện stale rõ ràng.
- [x] Không có OkHttp/WebSocket/Room/AI implementation trong slice mới.
- [x] Repository, ViewModel và UI state có test đáng tin cậy.
- [x] Build, unit test, lint và instrumentation test thành công.
- [x] Không triển khai feature ngoài TASK-003.

## Verification bắt buộc

```text
gradlew.bat --stop
gradlew.bat clean assembleDebug
gradlew.bat testDebugUnitTest
gradlew.bat lintDebug
gradlew.bat connectedDebugAndroidTest
```

Không đánh dấu `[x]` nếu command tương ứng chưa chạy thành công. Nếu file lock, Owner phải xử lý và chạy lại; static analysis không thay thế build/test.

## Ví dụ

Fake flow phát:

```text
[NGƯỜI KÝ] Xin chào.
[NGƯỜI NÓI] Chào bạn, bạn cần gì?
[NGƯỜI KÝ] Tôi muốn uống nước.
```

Sau khi flow chuyển `Disconnected`, màn hình vẫn giữ “Tôi muốn uống nước.” và hiển thị thời điểm cập nhật cuối cùng cùng nhãn mất kết nối.

## Handoff của Owner

### File đã sửa

- `com.example.smart_glass.domain.model`: `ConnectionState`, `RecognitionEvent`, `Speaker`.
- `com.example.smart_glass.domain.repository`: `RealtimeRepository`.
- `com.example.smart_glass.data.repository`: `FakeRealtimeRepository`.
- `com.example.smart_glass.feature.realtime`: `RealtimeUiState`, `RealtimeViewModel`, `RealtimeScreen`.
- `com.example.smart_glass.core.navigation`: Cấu hình `SmartGlassNavHost` để inject repository.
- `app/build.gradle.kts` & `libs.versions.toml`: Thêm `kotlinx-coroutines-test`.
- `app/src/test/java/com/example/smart_glass/`: `FakeRealtimeRepositoryTest`, `RealtimeViewModelTest`.
- `app/src/androidTest/java/com/example/smart_glass/feature/realtime/`: `RealtimeScreenTest`.

### Quyết định kỹ thuật

- **Unidirectional Data Flow**: ViewModel lắng nghe Flow từ Repository và cập nhật `StateFlow<RealtimeUiState>`.
- **Deterministic Fake**: `FakeRealtimeRepository` phát chuỗi "Tôi muốn uống nước" sau đó là câu phản hồi từ người nói, rồi ngắt kết nối.
- **UI Stale State**: Khi ngắt kết nối, chữ mờ đi (alpha 0.6) và hiển thị timestamp cập nhật cuối.
- **Basic DI**: Repository được khởi tạo và lưu giữ bằng `remember` trong `NavHost` và truyền vào ViewModel qua Factory.

### Kết quả build/test

- `.\gradlew.bat clean assembleDebug`: **BUILD SUCCESSFUL** (Sau khi xóa thủ công thư mục `build` do file lock).
- `.\gradlew.bat testDebugUnitTest`: **BUILD SUCCESSFUL** (6 tests passed: `AppBuildInfoTest`, `TopLevelDestinationTest`, `FakeRealtimeRepositoryTest`, `RealtimeViewModelTest`).
- `.\gradlew.bat lintDebug`: **BUILD SUCCESSFUL** (Report generated).
- `.\gradlew.bat connectedDebugAndroidTest`: **BUILD SUCCESSFUL** (2 tests passed trên `realme RMX1919`).

### Phần còn lại/blocker

- Không có.

## Review của Reviewer (Antigravity)

### Findings

-   **Architecture**: Tuân thủ Unidirectional Data Flow. Repository interface tách biệt tốt.
-   **Scope**: Không phát hiện rò rỉ network/database/AI logic vào layer này.
-   **Build/Test**: Đã kiểm tra evidence của Owner. 6 Unit Tests và 2 Instrumentation Tests bao phủ các logic quan trọng của Repository, ViewModel và UI state.
-   **Code Quality**: Cấu trúc package feature-first chuẩn mực. Sử dụng Material 3 tokens đồng nhất.
-   **Minor**: `RealtimeScreen.kt` có một số tham chiếu dùng fully qualified name (e.g. `com.example.smart_glass.domain.model.RecognitionEvent`), có thể cải thiện bằng cách import, nhưng không ảnh hưởng chức năng.

### Kết luận

`VERIFIED`

## Ghi chú triển khai

Android Studio Agent là writer duy nhất khi task `IN_PROGRESS`. Antigravity review sau `READY_FOR_REVIEW`. Codex không sửa Android source trong task này. Không dùng fake source để đánh dấu API/Pi là Implemented.

## Tài liệu liên quan

- [../WORKFLOW.md](../WORKFLOW.md)
- [../TASK_TEMPLATE.md](../TASK_TEMPLATE.md)
- [../../04_Android/IMPLEMENTATION_PLAN.md](../../04_Android/IMPLEMENTATION_PLAN.md)
- [../../04_Android/ANDROID_ARCHITECTURE.md](../../04_Android/ANDROID_ARCHITECTURE.md)
- [../../04_Android/DATA_FLOW.md](../../04_Android/DATA_FLOW.md)
- [../../04_Android/REPOSITORY_PATTERN.md](../../04_Android/REPOSITORY_PATTERN.md)
- [../../04_Android/SCREEN_SPECIFICATIONS.md](../../04_Android/SCREEN_SPECIFICATIONS.md)
- [../../04_Android/DESIGN_SYSTEM.md](../../04_Android/DESIGN_SYSTEM.md)
- [../../05_API/JSON_SCHEMA.md](../../05_API/JSON_SCHEMA.md)
- [../../99_Decisions/ADR-001.md](../../99_Decisions/ADR-001.md)
- [../../99_Decisions/ADR-004.md](../../99_Decisions/ADR-004.md)
