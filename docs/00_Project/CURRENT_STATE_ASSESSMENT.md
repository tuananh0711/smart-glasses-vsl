# Đánh giá hiện trạng repository

> Trạng thái: **Implemented**  
> Cập nhật: 2026-07-19

## Mục tiêu

Ghi lại kết quả khảo sát repository trước khi xây dựng tài liệu, phân biệt rõ kiến trúc mục tiêu và phần đã có bằng chứng triển khai.

## Phạm vi

Đã đọc theo thứ tự: `PROJECT_BRIEF_DAY_DU.md`, `PL2 - Anh - An.docx`, toàn bộ source/config Android, tìm kiếm toàn bộ source Raspberry Pi, cấu trúc thư mục, README và các tài liệu hiện có. Thư mục `Tham_khao` chỉ là tài liệu tham khảo hình thức/đồ án khóa trước, không phải nguồn kiến trúc dự án.

## Kiến trúc

Kiến trúc mục tiêu đúng là Edge AI: camera OV5647 hướng về người ký; Raspberry Pi thực hiện MediaPipe, normalization, GRU/TFLite, realtime recognition, Sentence Builder và phát âm thanh qua loa. Kính không có màn hình. REST/WebSocket và Android là nhánh phụ trợ để hiển thị văn bản. Repository hiện chưa chứa implementation cho pipeline này.

### Ma trận hiện trạng

| Thành phần | Trạng thái | Bằng chứng |
|---|---|---|
| Brief và PL2 | Implemented | Hai nguồn chính thức tồn tại và đã được đối chiếu |
| Android project skeleton | Implemented | Gradle, manifest, resources và test mẫu tồn tại |
| Android feature/UI/navigation/network | Planned | Không có `MainActivity` hay Kotlin production source |
| Raspberry Pi runtime | Planned | Không có file Python/service/config |
| Model GRU/TFLite, label map, metrics | Planned | Không có model hoặc training artifact |
| Dataset VSL400/Multi-VSL | Planned | Không có dataset/manifest trong repository |
| FastAPI/REST/WebSocket server | Planned | Không có server source hoặc schema thực thi |
| TTS/loa và hardware integration | Need Verification | Đầu ra chính đã được xác nhận là âm thanh qua loa, nhưng repository chưa có BOM, wiring hoặc driver source |
| Màn hình trên kính | Không áp dụng | Chủ dự án xác nhận ngày 2026-07-19 rằng kính không có màn hình; văn bản chỉ hiển thị trên Android |
| Test chức năng/hiệu năng | Planned | Chỉ có test template `2 + 2 = 4` và package-name test |

## Luồng hoạt động

Hiện tại chỉ có thể đọc và cấu hình skeleton Android; chưa có luồng end-to-end. Luồng mục tiêu được tài liệu hóa là camera -> landmark -> normalization -> GRU/TFLite -> smoothing -> Sentence Builder -> offline TTS/loa, đồng thời phát sự kiện văn bản tùy chọn sang Android.

## Ví dụ

Lệnh Gradle `tasks` đã tải wrapper 9.4.1 nhưng thất bại khi lưu configuration cache vì Kotlin Android plugin đăng ký task completion listener không được Gradle 9.4.1 hỗ trợ. Đây là bằng chứng build hiện tại chưa đạt, không phải lỗi của chức năng AI.

## Điểm mạnh

- Định hướng sản phẩm và ranh giới Edge AI được brief mô tả rất rõ.
- Pipeline landmark + GRU + TFLite phù hợp mục tiêu chạy trên Raspberry Pi hơn mô hình ảnh nặng.
- PL2 đã nêu phần cứng, luồng đa stage, smoothing, kiểm thử và kế hoạch tương đối đầy đủ.
- Android đã có nền Gradle/Compose, OkHttp và coroutines để tiếp tục phát triển companion app.

## Điểm yếu và phần còn thiếu

- Chưa có implementation Pi, AI, API, TTS/loa hoặc artifact model/dataset.
- Android chưa có entry activity và build toolchain đang không tương thích.
- Chưa có contract JSON, error taxonomy, versioning hay update/rollback thực thi.
- Chưa có benchmark chứng minh FPS/latency/accuracy, test offline autonomy hoặc soak test.
- PL2 còn mâu thuẫn nội bộ: 10-18 FPS/<=1 giây so với brief 15-30 FPS/<300 ms; TTS đôi lúc ở Pi, đôi lúc ở Android; bảng kế hoạch cũ còn nhắc YOLO; MQTT xuất hiện ở một màn hình dù kiến trúc chính chốt WebSocket.
- Chưa có thông số loa, mạch âm thanh/giao thức I2S được kiểm chứng, chính sách dữ liệu cá nhân và license dataset.

## Ghi chú triển khai

Thứ tự ưu tiên khi có mâu thuẫn: quyết định được chủ dự án xác nhận và ghi bằng ADR -> brief và phần kiến trúc Edge AI chính thức -> PL2 phần thiết kế hiện hành -> source/config -> tài liệu tham khảo. ADR-004 loại bỏ màn hình trên kính mà không thay đổi nguyên tắc Pi hoạt động độc lập. Các dòng YOLO/MQTT/Cloud từ biểu mẫu hoặc kế hoạch cũ không được dùng để thay đổi kiến trúc nếu chưa có ADR. Mọi mục chưa có source được giữ ở **Planned**; phần cứng/thông số chưa kiểm chứng dùng **Need Verification**.

## Tài liệu liên quan

- [README.md](README.md)
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
- [REQUIREMENTS.md](REQUIREMENTS.md)
- [../01_System/SYSTEM_ARCHITECTURE.md](../01_System/SYSTEM_ARCHITECTURE.md)
- [../99_Decisions/ADR-001.md](../99_Decisions/ADR-001.md)
- [../99_Decisions/ADR-004.md](../99_Decisions/ADR-004.md)
