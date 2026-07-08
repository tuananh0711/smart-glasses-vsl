# Kính Thông Minh Nhận Diện Ngôn Ngữ Ký Hiệu Tiếng Việt (VSL)

Dự án Đồ án Tốt nghiệp (KLTN) xây dựng hệ thống kính thông minh tích hợp trí tuệ nhân tạo (Edge AI) có khả năng dịch ngôn ngữ ký hiệu sang tiếng Việt hoàn toàn theo thời gian thực tại thiết bị (100% On-Device).

## 🌟 Điểm nổi bật của hệ thống
- **Edge Computing:** Toàn bộ quá trình xử lý (trích xuất đặc trưng & phân loại) diễn ra cục bộ trên vi mạch Raspberry Pi mà không cần kết nối Internet, đảm bảo tính di động và bảo mật tuyệt đối.
- **Tối ưu hóa Đặc trưng:** Sử dụng thuật toán MediaPipe Holistic, trích xuất chính xác 48 điểm đặc trưng 3D cốt lõi (2 tay và 6 điểm thân trên), loại bỏ hoàn toàn phần mặt và thân dưới để giảm nhiễu và tăng tốc độ xử lý.
- **Mô hình AI Siêu nhẹ:** Ứng dụng mạng nơ-ron hồi quy **GRU** kết hợp cùng TensorFlow Lite (TFLite) để đạt được sự cân bằng hoàn hảo giữa độ chính xác khi nhận diện 472 từ vựng động và khả năng tiêu thụ tài nguyên của phần cứng nhúng.

## 🛠️ Kiến trúc Hệ thống
1. **Phần cứng:** Kính đeo tay tích hợp camera góc rộng (OV5647) và vi điều khiển Raspberry Pi.
2. **Tiền xử lý (Preprocessing):** Trích xuất tọa độ 48 điểm từ các luồng video (sử dụng tập dữ liệu VSL400 mở rộng).
3. **Huấn luyện (Training):** Mô hình GRU nhận đầu vào là chuỗi thời gian (60 frames/từ).
4. **Suy luận (Inference):** Dùng Sliding Window để nhận diện ký hiệu liên tục trên luồng camera, phát âm thanh ra loa và đồng bộ kết quả (text) qua ứng dụng Android bằng kết nối không dây nội bộ.

## 📁 Cấu trúc Thư mục Code
```text
do_an_tot_nghiep/
├── src/
│   ├── preprocess.py       # Code trích xuất 48 điểm từ video MP4 sang file Numpy (.npy)
│   ├── data_loader.py      # Code load dữ liệu, mapping từ vựng và đẩy vào model
│   ├── model.py            # Khởi tạo kiến trúc và huấn luyện mạng GRU
│   └── inference_webcam.py # Code test nhận diện trực tiếp bằng webcam PC
├── data/
│   ├── classes.json        # File từ điển map index với từ vựng tiếng Việt
│   └── my_preprocessed/    # Thư mục lưu kết quả tiền xử lý (Sẽ tự tạo khi chạy code)
└── README.md
```

## 🚀 Hướng dẫn chạy dự án (Dành cho Team)

**1. Cài đặt môi trường:**
Máy tính cần sử dụng Python 3.8 - 3.12. Cài đặt các thư viện cần thiết:
```bash
pip install mediapipe==0.10.14
pip install tensorflow opencv-python numpy
```

**2. Quy trình huấn luyện mô hình:**
*   Chạy file tiền xử lý (nhớ tải raw video từ Drive bỏ vào thư mục `Dataset` trước):
    `python src/preprocess.py`
*   Chạy huấn luyện mô hình GRU:
    `python src/model.py`
*   Thử nghiệm inference trên webcam của Laptop:
    `python src/inference_webcam.py`
