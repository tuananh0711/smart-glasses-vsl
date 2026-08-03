# PROJECT BRIEF - ĐỒ ÁN TỐT NGHIỆP

## Tên đề tài

Kính thông minh hỗ trợ dịch ngôn ngữ ký hiệu tiếng Việt theo thời gian
thực sử dụng Raspberry Pi và Trí tuệ nhân tạo

# 1. Mục tiêu đề tài

Xây dựng một hệ thống kính thông minh hỗ trợ người nghe giao tiếp với
người khiếm thính.

Người khiếm thính sử dụng ngôn ngữ ký hiệu.

Người nghe đeo kính thông minh.

Camera trên kính sẽ quan sát người ký và dịch toàn bộ cử chỉ sang tiếng
Việt hiển thị ngay trên màn hình của kính và ứng dụng Android.

Hệ thống phải hoạt động gần thời gian thực và có khả năng mở rộng số
lượng ký hiệu sau này.

# 2. Định hướng cuối cùng của đề tài

Không chỉ nhận diện từng ký hiệu riêng lẻ.

Mục tiêu cuối cùng là:

dịch liên tục một đoạn hội thoại từ ngôn ngữ ký hiệu sang câu tiếng
Việt.

Ví dụ

Người ký:

"Tôi muốn uống nước"

Kết quả hiển thị

"Tôi muốn uống nước."

Thay vì

Tôi 
Muốn 
Uống 
Nước

Hệ thống cần có khả năng ghép chuỗi ký hiệu thành câu hoàn chỉnh.

# 3. Đối tượng sử dụng

Người nghe bình thường đeo kính.

Người khiếm thính đứng đối diện và thực hiện ngôn ngữ ký hiệu.

Camera không nhìn xuống tay người đeo kính.

Camera nhìn người ký phía trước.

# 4. Phần cứng

Thiết bị xử lý

Raspberry Pi 4 Model B

RAM 8GB

Ubuntu Server

TensorFlow Lite

MediaPipe

Camera

Raspberry Pi Camera OV5647

Góc rộng 120°

Camera đặt trên kính.

Góc nhìn hướng về phía người ký.

Thiết bị hiển thị

Màn hình nhỏ gắn trên kính

Đồng thời gửi dữ liệu sang ứng dụng Android.

# 5. Kiến trúc hệ thống

Camera

↓

MediaPipe

↓

Landmark Extraction

↓

Normalize Landmark

↓

GRU Sequence Model

↓

TensorFlow Lite

↓

Realtime Prediction

↓

Sentence Builder

↓

Android App + Glass Display

# 6. Hướng AI

KHÔNG sử dụng YOLO làm mô hình chính.

YOLO chỉ dùng nếu sau này cần phát hiện người.

Mô hình chính gồm:

MediaPipe

↓

Landmark

↓

GRU

↓

TensorFlow Lite

Lý do

chạy nhanh trên Raspberry Pi ít tài nguyên ổn định phù hợp chuỗi thời
gian

# 7. Input của mô hình

MediaPipe Hands

MediaPipe Pose

(có thể mở rộng Face sau này)

Mỗi frame lưu landmark.

Không đưa ảnh trực tiếp vào mô hình.

Chỉ đưa landmark.

# 8. Dataset

Định hướng sử dụng

VSL400

Là bộ dữ liệu chính.

Có thể mở rộng sang

Multi-VSL

Nếu đủ tài nguyên.

Trong giai đoạn đầu có thể dùng tập con để xây dựng pipeline.

# 9. Mục tiêu số lượng ký hiệu

Mục tiêu triển khai

Khoảng 400 ký hiệu

Mục tiêu mở rộng

Khoảng 1000 ký hiệu

Không giới hạn kiến trúc ở 400 ký hiệu.

Mọi thành phần phải có khả năng mở rộng.

# 10. Các giai đoạn AI

Giai đoạn 1

Extract landmark

↓

Train GRU

↓

Kiểm tra Accuracy

↓

Convert TensorFlow Lite

↓

Deploy Raspberry Pi

Giai đoạn 2

Realtime Recognition

Camera

↓

MediaPipe

↓

GRU

↓

Prediction

Giai đoạn 3

Continuous Recognition

Thay vì nhận từng từ.

Mô hình nhận chuỗi ký hiệu.

Giai đoạn 4

Sentence Builder

Ghép các ký hiệu thành câu.

Ví dụ

Tôi

Muốn

Đi

Học

↓

Tôi muốn đi học.

# 11. Android App

Android App KHÔNG xử lý AI.

Android App chỉ là giao diện.

App nhận dữ liệu từ Raspberry Pi.

Hiển thị

Camera Preview (nếu cần) Landmark Debug Ký hiệu vừa nhận Câu hoàn chỉnh
Lịch sử hội thoại Kết nối Raspberry Pi Cấu hình camera Cập nhật model
Kiểm tra FPS Kiểm tra độ trễ

Toàn bộ AI chạy trên Raspberry Pi.

# 12. Raspberry Pi chịu trách nhiệm

MediaPipe

Inference

TensorFlow Lite

Prediction

Sentence Builder

API

Streaming

Android chỉ hiển thị.

# 13. Hiệu năng mong muốn

FPS

# 15--30 FPS

Độ trễ

\<300ms

Realtime.

# 14. Nguyên tắc thiết kế

Ưu tiên

Realtime

Ổn định

Ít tài nguyên

Có khả năng mở rộng

Có thể train lại

Có thể cập nhật model

Có thể thay đổi dataset

Không phụ thuộc Android.

# 15. Công nghệ

Ubuntu

Python

TensorFlow

TensorFlow Lite

MediaPipe

OpenCV

NumPy

FastAPI

WebSocket

Android Kotlin

Jetpack Compose

CameraX

Material 3

Git

GitHub

# 16. Phân chia công việc

Người 1 (AI Team)

Chuẩn hóa dataset Trích xuất landmark Huấn luyện mô hình GRU Đánh giá
Accuracy Chuyển TensorFlow Lite Tối ưu mô hình cho Raspberry Pi Xây dựng
API suy luận

Người 2 (Android Team)

Thiết kế giao diện bằng Jetpack Compose Quản lý kết nối tới Raspberry Pi
(REST/WebSocket) Hiển thị kết quả nhận diện theo thời gian thực Hiển thị
lịch sử hội thoại Quản lý cấu hình và trạng thái kết nối Tích hợp
Text-to-Speech (nếu cần) Chuẩn bị sẵn giao diện để sau này bổ sung các
tính năng mới

# 17. Điều quan trọng nhất

Không muốn làm một đồ án chỉ nhận diện từng ký hiệu.

Muốn xây dựng một hệ thống gần với sản phẩm thực tế:

Người nghe đeo kính → người khiếm thính ký → hệ thống nhận diện liên tục
→ ghép thành câu → hiển thị ngay trên kính và ứng dụng Android.

Prompt dùng cho chat mới (để AI tư vấn app Android)

Tôi đang thực hiện đồ án tốt nghiệp về kính thông minh dịch ngôn ngữ ký
hiệu tiếng Việt. Hệ thống gồm Raspberry Pi 4 8GB, camera OV5647 góc rộng
120°, MediaPipe để trích xuất landmark, mô hình GRU chạy bằng TensorFlow
Lite trên Raspberry Pi. AI xử lý hoàn toàn trên Raspberry Pi; ứng dụng
Android chỉ đóng vai trò giao diện hiển thị, cấu hình và giao tiếp với
Raspberry Pi qua REST/WebSocket. Mục tiêu cuối cùng là nhận diện khoảng
400 ký hiệu (có khả năng mở rộng lên 1000), dịch liên tục thành câu
tiếng Việt và hiển thị theo thời gian thực. Hãy đóng vai trò là Senior
Android Architect và đề xuất kiến trúc ứng dụng, các màn hình, luồng dữ
liệu, giao diện người dùng, API cần thiết và những tính năng giúp sản
phẩm giống một thiết bị thương mại thay vì chỉ là ứng dụng demo.

Prompt này sẽ giúp AI mới hiểu đúng định hướng của dự án và tập trung
vào phần Android mà không đề xuất những hướng đi lệch với kiến trúc bạn
đã thống nhất.
# Kiến trúc và triết lý thiết kế của dự án (Quan trọng)

## Định hướng cốt lõi

Đây là một dự án **Edge AI**, không phải Cloud AI.

Mục tiêu của hệ thống là toàn bộ quá trình xử lý AI phải được thực hiện trực tiếp trên Raspberry Pi mà không phụ thuộc vào Internet hoặc dịch vụ điện toán đám mây.

Hệ thống phải có khả năng hoạt động độc lập trong môi trường không có kết nối mạng.

Nếu mất Internet, mất WiFi hoặc không có điện thoại Android, hệ thống vẫn phải nhận diện và dịch ngôn ngữ ký hiệu bình thường.

Đây là yêu cầu thiết kế quan trọng nhất của toàn bộ đồ án.

---

## Vai trò của Raspberry Pi

Raspberry Pi là trung tâm của toàn bộ hệ thống.

Raspberry Pi chịu trách nhiệm:

- Thu nhận hình ảnh từ camera OV5647.
- Tiền xử lý dữ liệu.
- Trích xuất MediaPipe Landmark.
- Chuẩn hóa Landmark.
- Chạy mô hình AI TensorFlow Lite.
- Nhận diện ký hiệu.
- Nhận diện liên tục theo thời gian thực.
- Ghép các ký hiệu thành câu hoàn chỉnh (Sentence Builder).
- Hiển thị kết quả lên màn hình gắn trên kính.
- Cung cấp API (REST/WebSocket) nếu có thiết bị ngoài kết nối.

Toàn bộ AI chạy trên Raspberry Pi.

Không sử dụng Cloud AI cho quá trình suy luận (Inference).

---

## Vai trò của Android

Android KHÔNG phải là thành phần chính của hệ thống.

Android chỉ đóng vai trò hỗ trợ.

Các chức năng của Android gồm:

- Hiển thị kết quả nhận diện.
- Hiển thị câu hoàn chỉnh.
- Hiển thị lịch sử hội thoại.
- Theo dõi trạng thái Raspberry Pi.
- Cấu hình hệ thống.
- Cập nhật model AI.
- Cập nhật cấu hình.
- Debug.
- Kiểm tra FPS và độ trễ.

Nếu Android không tồn tại hoặc mất kết nối thì Raspberry Pi vẫn phải hoạt động bình thường.

Không được thiết kế kiến trúc phụ thuộc Android.

---

## Vai trò của Internet

Internet không phải yêu cầu bắt buộc.

Internet chỉ được sử dụng nếu sau này bổ sung các tính năng như:

- Đồng bộ dữ liệu.
- Sao lưu.
- Cập nhật phần mềm.
- Cập nhật mô hình AI.
- Quản lý từ xa.

Các chức năng nhận diện ngôn ngữ ký hiệu tuyệt đối không phụ thuộc Internet.

---

## Kiến trúc xử lý

```text
Camera OV5647
        │
        ▼
Raspberry Pi 4 (Edge AI)
        │
        ├── Video Capture
        ├── MediaPipe
        ├── Landmark Extraction
        ├── Landmark Normalization
        ├── TensorFlow Lite Inference
        ├── Continuous Recognition
        ├── Sentence Builder
        ├── Glass Display
        └── REST/WebSocket Server
                    │
          (Tùy chọn nếu có)
                    ▼
             Android Application
```

Android là thiết bị phụ trợ, không phải trung tâm của hệ thống.

---

## Nguyên tắc thiết kế

Mọi đề xuất trong quá trình phát triển phải tuân theo các nguyên tắc sau:

1. Ưu tiên xử lý tại biên (Edge AI).
2. Không phụ thuộc Internet.
3. Không phụ thuộc Cloud AI.
4. Không phụ thuộc Android.
5. Độ trễ thấp.
6. Hoạt động gần thời gian thực.
7. Tiết kiệm tài nguyên Raspberry Pi.
8. Có khả năng mở rộng lên khoảng 1000 ký hiệu.
9. Có thể huấn luyện lại khi có dataset mới.
10. Có thể cập nhật mô hình TensorFlow Lite mà không cần thay đổi kiến trúc hệ thống.

---

## Khi đưa ra đề xuất

Khi đề xuất giải pháp, kiến trúc hoặc thuật toán, hãy luôn ưu tiên:

- Khả năng chạy trực tiếp trên Raspberry Pi 4 (RAM 8GB).
- Hiệu năng thời gian thực.
- Tiết kiệm CPU và RAM.
- TensorFlow Lite.
- MediaPipe Landmark.
- GRU/LSTM hoặc các mô hình chuỗi nhẹ phù hợp với Edge AI.

Không đề xuất các mô hình hoặc kiến trúc chỉ phù hợp khi chạy trên GPU mạnh hoặc Cloud Server nếu không thực sự cần thiết.

Mục tiêu cuối cùng của đồ án là xây dựng một thiết bị kính thông minh có thể hoạt động như một sản phẩm thực tế, trong đó Raspberry Pi là bộ não của toàn bộ hệ thống và có thể hoạt động độc lập trong môi trường không có Internet.