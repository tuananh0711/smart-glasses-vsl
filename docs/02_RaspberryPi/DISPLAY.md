# Chính sách đầu ra âm thanh và hiển thị

> Trạng thái: **Implemented**  
> Cập nhật: 2026-07-19

## Mục tiêu

Ghi nhận quyết định không trang bị màn hình trên kính và phân định đầu ra âm thanh trên Pi với hiển thị văn bản trên Android.

## Phạm vi

Kính không có màn hình. Raspberry Pi phát kết quả chủ yếu bằng offline TTS qua loa; Android chỉ hiển thị văn bản khi kết nối. Pi vẫn phải hoàn thành nhận diện và phát âm thanh khi Android không tồn tại.

## Kiến trúc

Audio adapter trên Pi tiêu thụ sentence event, thực hiện offline TTS và xuất qua giao tiếp âm thanh/loa. API adapter có thể đồng thời gửi sentence event sang Android để hiển thị.

## Luồng hoạt động

Sentence accepted -> offline TTS -> audio output. Song song: sentence event -> WebSocket -> Android text UI nếu có client.

## Ví dụ

Mất app/Wi-Fi, Pi vẫn phát câu nhận diện qua loa; không có màn hình văn bản cục bộ trên kính.

## Ghi chú triển khai

Loại loa, MAX98357A/I2S, TTS engine và wiring cụ thể vẫn là **Need Verification** vì chưa có source hoặc BOM kiểm chứng. Quyết định không có màn hình trên kính đã được xác nhận và ghi tại ADR-004.

Quy ước trạng thái: **Planned** khi mới là thiết kế; **Implemented** khi có bằng chứng source/config; **Need Verification** khi repository chưa đủ bằng chứng hoặc nguồn còn mâu thuẫn. Khi triển khai, phải bổ sung liên kết source và test evidence vào file này.

## Tài liệu liên quan

- [PI_ARCHITECTURE.md](PI_ARCHITECTURE.md)
- [../99_Decisions/ADR-001.md](../99_Decisions/ADR-001.md)
- [../99_Decisions/ADR-004.md](../99_Decisions/ADR-004.md)
