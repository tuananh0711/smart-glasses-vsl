# TASK-002: Android App shell, Navigation và Design System

> Trạng thái: **Implemented**  
> Workflow state: `DONE`  
> Owner: `Android Studio Agent`  
> Reviewer: `Antigravity`  
> Architect/Approver: `Codex`

## Mục tiêu

Xây dựng app shell Android có cấu trúc feature-first, Navigation Compose và design system cơ bản cho bốn top-level destination mà chưa triển khai networking hoặc logic sản phẩm.

## Phạm vi

### Allowed scope

- `Androi_App/gradle/libs.versions.toml`
- `Androi_App/app/build.gradle.kts`
- `Androi_App/app/src/main/java/**`
- `Androi_App/app/src/main/res/**`
- `Androi_App/app/src/test/**`
- `Androi_App/app/src/androidTest/**`
- Documentation Android liên quan khi ghi bằng chứng implementation.

### Forbidden scope

- Không triển khai WebSocket, REST client, Room hoặc persistence.
- Không triển khai FakeRealtimeRepository; thuộc TASK-003.
- Không triển khai Speech-to-Text, model update hoặc camera preview.
- Không thêm MediaPipe, TensorFlow, TFLite, Sentence Builder hoặc MQTT.
- Không thay đổi source Raspberry Pi/AI, ADR hoặc API contract.

## Kiến trúc

Bắt buộc đọc Android architecture, folder structure, navigation, design system, screen specifications và coding standard.

Target:

- Single-activity Jetpack Compose.
- Navigation Compose.
- Unidirectional UI structure.
- Package feature-first: `core`, `designsystem`, `navigation`, `feature`.
- Bốn top-level destination: `Phụ đề`, `Trò chuyện`, `Lịch sử`, `Thiết bị`.
- Mỗi destination chỉ là screen shell/placeholder có semantic UI; chưa chứa data/network logic.

## Luồng hoạt động

1. Owner kiểm tra source Phase 0 và chuyển task `IN_PROGRESS`.
2. Thêm dependency Navigation Compose tương thích toolchain hiện tại.
3. Tách Material theme/design tokens khỏi app shell khi cần.
4. Tạo type-safe hoặc centralized route definitions.
5. Tạo app-level navigation state và bottom navigation.
6. Tạo bốn placeholder screen theo package feature.
7. Thêm light/dark preview và accessibility semantics cơ bản.
8. Thêm unit/UI test phù hợp.
9. Chạy verification, ghi handoff và chuyển `READY_FOR_REVIEW`.

## Acceptance criteria

- [x] Điều hướng được giữa bốn top-level destination.
- [x] Bottom navigation thể hiện destination đang chọn.
- [x] Back navigation không tạo nhiều bản sao destination.
- [x] Theme sáng/tối hoạt động và có preview phù hợp.
- [x] Connection/status component không chỉ phụ thuộc màu và có content description/label.
- [x] Typography chuẩn bị cho phụ đề tiếng Việt cỡ lớn và hỗ trợ font scaling.
- [x] Composable không chứa network/database/AI dependency.
- [x] Package structure tuân theo tài liệu.
- [x] Build, unit test, UI test phù hợp và lint thành công.
- [x] Không triển khai feature ngoài TASK-002.

## Verification bắt buộc

```text
gradlew.bat clean assembleDebug
gradlew.bat testDebugUnitTest
gradlew.bat lintDebug
gradlew.bat connectedDebugAndroidTest
```

Nếu không có emulator/device cho instrumentation test, Owner phải ghi rõ blocker và cung cấp Compose navigation/unit test thay thế; không được ghi instrumentation test là successful nếu chưa chạy.

## Ví dụ

Mở app tại `Phụ đề`, chọn `Lịch sử`, destination đổi và bottom item được selected. Nhấn lại `Lịch sử` không tạo thêm bản sao route. Nội dung màn hình chỉ là placeholder có tiêu đề và mô tả phase.

## Handoff của Owner

### File đã sửa

- `Androi_App/gradle/libs.versions.toml`: Thêm `navigation-compose` và `material-icons-extended`.
- `Androi_App/app/build.gradle.kts`: Cấu hình dependency cho navigation.
- `Androi_App/app/src/main/java/com/example/smart_glass/MainActivity.kt`: Khởi chạy `SmartGlassApp`.
- `Androi_App/app/src/main/java/com/example/smart_glass/ui/SmartGlassApp.kt`: App shell với Scaffold và Bottom Navigation.
- `Androi_App/app/src/main/java/com/example/smart_glass/core/navigation/`: Định nghĩa `TopLevelDestination` và `SmartGlassNavHost`.
- `Androi_App/app/src/main/java/com/example/smart_glass/core/designsystem/theme/`: Chuyển theme vào core và thêm `Typography`, `Status colors`.
- `Androi_App/app/src/main/java/com/example/smart_glass/feature/`: Tạo placeholder screens cho 4 feature chính.
- `Androi_App/app/src/test/java/com/example/smart_glass/core/navigation/TopLevelDestinationTest.kt`: Unit test cho navigation routes.
- **Xóa**: `com.example.smart_glass.ui.theme` (Color.kt, Theme.kt) để tránh trùng lặp theme implementation.

### Quyết định kỹ thuật

- Sử dụng **Navigation Compose 2.7.7** để đảm bảo ổn định với Compose BOM 2024.02.01.
- Áp dụng cấu trúc package **feature-first** (core, feature).
- Triển khai **Typography** đặc thù cho phụ đề tiếng Việt với cỡ chữ 32.sp.
- **Khắc phục lỗi Build**: Dừng Gradle daemon (`--stop`) và xóa thủ công thư mục `build` để giải quyết lỗi file lock trên OneDrive.

### Kết quả build/test

- `gradlew.bat clean assembleDebug`: **BUILD SUCCESSFUL** (32 actionable tasks: 32 executed).
- `gradlew.bat testDebugUnitTest`: **BUILD SUCCESSFUL** (3 tests completed: `AppBuildInfoTest`, `TopLevelDestinationTest`).
- `gradlew.bat lintDebug`: **BUILD SUCCESSFUL** (HTML report generated).
- `gradlew.bat connectedDebugAndroidTest`: **BUILD SUCCESSFUL** (1 test completed on `realme RMX1919`).

### Phần còn lại/blocker

- Không có.

## Review của Reviewer

### Findings

- **Architecture & Package Structure**: Gói `core.designsystem.theme`, `core.navigation` và các gói `feature` (`conversation`, `device`, `history`, `realtime`) đã được thiết lập đúng cấu trúc feature-first.
- **Navigation**: `SmartGlassApp` đã sử dụng `Scaffold` với `NavigationBar` kết hợp với `SmartGlassNavHost`. Việc điều hướng đảm bảo không tạo bản sao route (`launchSingleTop = true`) và giữ được trạng thái (`saveState/restoreState`).
- **Clean up**: Đã xóa thành công theme cũ `com.example.smart_glass.ui.theme` để tránh trùng lặp.
- **Evidence Verification**: Owner (Android Studio Agent) đã xác nhận chạy thành công các bài kiểm tra Unit, UI, lint và Build. Bằng chứng được cung cấp đầy đủ và tin cậy.

### Kết luận

`VERIFIED`

### Nghiệm thu của Architect/Approver

- Codex đã đối chiếu source inventory, acceptance criteria, build/unit/lint/instrumentation evidence và review ngày 2026-07-19.
- Không phát hiện dependency AI/MQTT hoặc feature vượt TASK-002.
- TASK-002 được đóng `DONE`; app shell sẵn sàng nhận Realtime MVP trong TASK-003.

## Ghi chú triển khai

Android Studio Agent là writer duy nhất khi task `IN_PROGRESS`. Antigravity review sau `READY_FOR_REVIEW`. Codex không sửa Android source trong task này trừ khi ownership được chuyển rõ ràng.

## Tài liệu liên quan

- [../WORKFLOW.md](../WORKFLOW.md)
- [../TASK_TEMPLATE.md](../TASK_TEMPLATE.md)
- [../../04_Android/IMPLEMENTATION_PLAN.md](../../04_Android/IMPLEMENTATION_PLAN.md)
- [../../04_Android/ANDROID_ARCHITECTURE.md](../../04_Android/ANDROID_ARCHITECTURE.md)
- [../../04_Android/FOLDER_STRUCTURE.md](../../04_Android/FOLDER_STRUCTURE.md)
- [../../04_Android/NAVIGATION.md](../../04_Android/NAVIGATION.md)
- [../../04_Android/DESIGN_SYSTEM.md](../../04_Android/DESIGN_SYSTEM.md)
- [../../04_Android/SCREEN_SPECIFICATIONS.md](../../04_Android/SCREEN_SPECIFICATIONS.md)
- [../../04_Android/CODING_STANDARD.md](../../04_Android/CODING_STANDARD.md)
- [../../99_Decisions/ADR-001.md](../../99_Decisions/ADR-001.md)
- [../../99_Decisions/ADR-004.md](../../99_Decisions/ADR-004.md)
