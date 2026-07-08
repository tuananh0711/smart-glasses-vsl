# TỔNG QUAN CỐT LÕI ĐỒ ÁN: KÍNH THÔNG MINH NHẬN DIỆN VSL

Tài liệu này tổng hợp **toàn bộ những quyết định kỹ thuật cốt lõi nhất** của dự án. Dùng để làm kim chỉ nam cho team khi code và là dàn ý chính để viết Báo Cáo Khóa Luận. Bất cứ khi nào bí ý tưởng hoặc quên logic, hãy mở file này ra xem lại!

---

## 1. Hướng đi cốt lõi (Kiến trúc hệ thống)
*   **Chốt hạ:** `100% On-Device Edge Computing` (Xử lý toàn bộ tại biên).
*   **Ý nghĩa:** Kính Raspberry Pi tự quay video, tự trích xuất đặc trưng, tự đưa vào model AI dự đoán và tự phát ra loa/màn hình mà **KHÔNG CẦN KẾT NỐI INTERNET**.
*   **Điểm ăn tiền bảo vệ trước hội đồng:** Bảo mật tuyệt đối hình ảnh người khuyết tật, độ trễ ổn định (không phụ thuộc mạng wifi yếu/mạnh), tính di động cực cao.

## 2. Tiền xử lý dữ liệu (MediaPipe Holistic)
Thay vì lấy toàn bộ 76 điểm (làm hệ thống Raspberry Pi bị quá tải và chậm), team đã quyết định **cắt giảm tối đa phần nhiễu**, chỉ giữ lại **48 điểm cốt lõi**:
*   **Bỏ:** Toàn bộ điểm khuôn mặt (tránh nhiễu khi đeo khẩu trang, tóc che mặt) và thân dưới (chân).
*   **Giữ lại:**
    *   21 điểm bàn tay trái.
    *   21 điểm bàn tay phải.
    *   6 điểm thân trên (2 vai, 2 khuỷu tay, 2 cổ tay) để xác định biên độ vung tay.
*   **Lợi ích:** Tăng FPS cho camera, giảm dung lượng tính toán, model học nhanh và tập trung đúng vào cử chỉ tay thay vì bị phân tâm bởi nét mặt.

## 3. Mô hình Trí tuệ Nhân tạo (AI Model)
*   **Mô hình được chọn:** Mạng nơ-ron hồi quy **GRU (Gated Recurrent Unit)**.
*   **Tại sao chọn GRU thay vì LSTM?** 
    *   GRU có cấu trúc cổng (gates) ít hơn LSTM, giúp giảm đáng kể số lượng tham số tính toán.
    *   Giúp tốc độ nhận diện (Inference) trên Raspberry Pi nhanh và mượt mà hơn rất nhiều, phù hợp với tiêu chí On-Device.
*   **Kỹ thuật ép xung (Tối ưu hóa):** Sau khi train xong file GRU gốc (`.keras` / `.h5`), mô hình sẽ được nén (Quantization) sang định dạng **TensorFlow Lite (`.tflite`)** để Raspberry Pi có thể load nhẹ nhàng vào RAM.

## 4. Đầu vào và Đầu ra (Input/Output)
*   **Dataset:** Dựa trên bộ VSL400 (có mở rộng), tổng cộng **472 từ vựng** ngôn ngữ ký hiệu tiếng Việt độc lập.
*   **Input (Đầu vào model):** Một ma trận chuỗi thời gian (Time-series) gồm **60 frames** (khung hình). Mỗi frame chứa tọa độ XYZ của 48 điểm (48 x 3 = 144 giá trị). Tóm lại Input Shape là `(60, 144)`.
*   **Output (Đầu ra):** Xác suất của 472 từ vựng (dùng hàm Softmax). Từ nào có % cao nhất sẽ được chọn làm kết quả.
*   **Sliding Window (Cửa sổ trượt):** Trong thực tế, camera quay liên tục 30 FPS. Thuật toán sẽ lưu lại 60 frame gần nhất vào một hàng đợi (Queue). Cứ mỗi frame mới xuất hiện, frame cũ nhất bị đẩy ra, tạo thành một dòng chảy dữ liệu liên tục đưa vào AI dự đoán (Giúp nhận diện mượt mà không bị ngắt quãng).
