# 👓 Kính Thông Minh Nhận Diện & Dịch Ngôn Ngữ Ký Hiệu Tiếng Việt (VSL)

> **Hệ thống Kính Thông Minh Hỗ Trợ Giao Tiếp Cho Người Khiếm Thính Bằng Trí Tuệ Nhân Tạo Biên (Real-time Edge AI Vietnamese Sign Language Smart Glasses)**  
> *Đồ án Tốt nghiệp Kỹ sư / Cử nhân Công nghệ Thông tin*

---

## 📌 Giới thiệu Đề tài

Dự án nghiên cứu và phát triển một hệ thống **Kính Mắt Thông Minh (Smart Glasses)** tích hợp **Trí tuệ nhân tạo tại biên (Edge AI)** nhằm phá vỡ rào cản giao tiếp giữa người khiếm thính (sử dụng Ngôn ngữ Ký hiệu Tiếng Việt - VSL) và người bình thường (người nghe/nói).

### 🔄 Mô hình Tương tác Thực tế
* **Người nghe bình thường** đeo kính thông minh có gắn camera góc rộng (120° FOV) ở vị trí gọng kính, góc nhìn hướng thẳng về phía người đối diện.
* **Người khiếm thính** đứng đối diện và thực hiện các động tác ngôn ngữ ký hiệu tự nhiên trong tầm quan sát của camera.
* **Bộ não xử lý (Raspberry Pi 4)** tiếp nhận luồng hình ảnh, nhận diện chuỗi cử chỉ và ghép thành câu tiếng Việt hoàn chỉnh theo thời gian thực **100% On-Device (Offline)** mà không cần kết nối Internet hoặc Cloud Server.
* **Đầu ra chính (ADR-004):** Câu hoàn chỉnh được phát âm thanh trực tiếp qua **Loa tích hợp trên kính** bằng công nghệ Chuyển văn bản thành giọng nói Offline (Offline TTS), giúp người nghe hiểu ngay lập tức mà không cần cúi nhìn màn hình. **Kính hoàn toàn không gắn màn hình hiển thị (HUD)** để tối ưu trọng lượng, không gây nhiệt ở vùng mắt và tiết kiệm điện năng.
* **Thiết bị đồng hành phụ trợ (Android Companion App):** Khi người dùng muốn xem phụ đề dạng chữ (subtitles) hoặc lưu lại lịch sử hội thoại, ứng dụng Android kết nối với Wi-Fi nội bộ của Raspberry Pi qua WebSocket/REST API để hiển thị văn bản thời gian thực và hỗ trợ người nghe gõ text phản hồi. Kính hoàn toàn độc lập và hoạt động bình thường ngay cả khi không có điện thoại bên cạnh.

---

## 🌟 Điểm Nổi Bật Của Hệ Thống

* **⚡ 100% Edge AI & Offline First (ADR-001):** Toàn bộ pipeline từ thu nhận hình ảnh, trích xuất đặc trưng, suy luận mô hình học sâu, lọc nhiễu, ghép câu đến phát âm thanh đều chạy cục bộ trên Raspberry Pi 4. Đảm bảo bảo mật hình ảnh cá nhân tuyệt đối, độ trễ thấp và hoạt động ở bất kỳ đâu không phụ thuộc Internet.
* **🎯 Tối ưu hóa Đặc trưng (MediaPipe 48 Landmarks):** Sử dụng thuật toán MediaPipe Holistic, trích xuất chính xác **48 điểm đặc trưng 3D cốt lõi** (42 điểm của 2 bàn tay + 6 điểm khung thân trên: hai vai, hai khuỷu tay, hai cổ tay). Hệ thống loại bỏ hoàn toàn phần mặt và chân, giúp giảm hơn 70% dữ liệu dư thừa, triệt tiêu nhiễu bối cảnh và đảm bảo tốc độ xử lý cao trên phần cứng nhúng.
* **📐 Chuẩn hóa Tọa độ Bất biến (Scale & Translation Invariant Normalization):**
  * *Tịnh tiến (Translation):* Đưa trung điểm hai vai về gốc tọa độ `(0, 0, 0)` để triệt tiêu sai số vị trí đứng trong khung hình.
  * *Co giãn (Scale):* Chuẩn hóa kích thước khung xương theo khoảng cách giữa 2 vai, giúp mô hình nhận diện chính xác dù người ký đứng gần hay xa camera.
  * *Bù khuyết (Imputation):* Tự động điền vector 0 cho các điểm bị che khuất tạm thời.
* **🧠 Mô hình Học sâu BiGRU Attention Siêu nhẹ:**
  * Tiếp nhận chuỗi đặc trưng thời gian (Sliding Window 60 frames/từ).
  * Ứng dụng mạng nơ-ron hồi quy **Bidirectional GRU** kết hợp cơ chế **Multi-Head Self-Attention** giúp mô hình tập trung vào các thời điểm thực hiện nét ký hiệu quan trọng nhất.
  * Nhận diện bộ từ điển **473 từ vựng VSL** thông dụng (`models/classes.json`).
  * Đã tối ưu hóa lượng tử hóa Dynamic Range sang **TensorFlow Lite (`.tflite`)**, nén kích thước mô hình xuống chỉ còn **~1.20 MB**, tải tensor cực nhanh và suy luận mượt mà trên CPU ARM của Raspberry Pi.
* **🗣️ Máy Trạng Thái 4 Pha & Xây Dựng Câu Tự Nhiên (Sentence Builder):**
  * Tích hợp máy trạng thái 4 pha (`IDLE -> ARMING -> RECORDING -> FINALIZING -> COOLDOWN`) tự động phát hiện chuyển động bắt đầu ký và thời điểm buông tay nghỉ.
  * Bộ lọc kép (*Confidence Threshold* & *Debounce Filter*) loại bỏ hoàn toàn hiện tượng nhấp nháy từ, dự đoán sai do chuyển tiếp giữa các cử chỉ.
  * Ghép các từ nhận diện thành câu tiếng Việt hoàn chỉnh (VD: *"Tôi"* + *"Muốn"* + *"Uống"* + *"Nước"* ➔ *"Tôi muốn uống nước."*) và phát âm thanh liền mạch.

---

## 🏗️ Kiến Trúc Hệ Thống & Luồng Dữ Liệu

### 1. Sơ Đồ Khối Tổng Thể
```text
      [CAMERA OV5647 120° FOV] (Gắn trên gọng kính, nhìn người ký)
                 │  (Luồng video 15-30 FPS)
                 ▼
┌─────────────────────────────────────────────────────────────┐
│          RASPBERRY PI 4 (EDGE AI - OFFLINE FIRST)           │
│                                                             │
│  [1. THU NHẬN & TIỀN XỬ LÝ]                                 │
│   └── Camera Capture (Picamera2 / OpenCV) -> BGR/RGB Frame  │
│                                                             │
│  [2. TRÍCH XUẤT ĐẶC TRƯNG & CHUẨN HÓA]                      │
│   ├── MediaPipe Holistic Tracker                            │
│   ├── Trích xuất 48 điểm 3D cốt lõi (144 features/frame)    │
│   └── Chuẩn hóa tọa độ theo vai (Scale & Translation norm)  │
│                                                             │
│  [3. SUY LUẬN MÔ HÌNH HỌC SÂU (DEEP LEARNING)]              │
│   ├── Cửa sổ thời gian trượt (Sliding Window 60 frames)     │
│   ├── TensorFlow Lite Interpreter (BiGRU Attention TFLite)  │
│   └── Phân loại xác suất 473 từ vựng VSL                    │
│                                                             │
│  [4. HẬU XỬ LÝ & BỘ XÂY DỰNG CÂU (SENTENCE BUILDER)]        │
│   ├── Bộ lọc ngưỡng tin cậy & Debounce Filter (Chống lặp)   │
│   ├── 4-State Machine (Nhận diện bắt đầu & hạ tay ngắt câu) │
│   └── Ghép chuỗi từ vựng thành câu tiếng Việt hoàn chỉnh    │
│                                                             │
│  [5. GIAO DIỆN ĐẦU RA]                                      │
│   ├── Offline TTS Engine (pyttsx3)                          │
│   └── FastAPI + WebSocket Server (Gửi dữ liệu qua Wi-Fi)    │
└─────────┬───────────────────────────┬───────────────────────┘
          │ (Âm thanh phát loa)       │ (JSON phụ đề thời gian thực)
          ▼                           ▼
    [LOA TÍCH HỢP]              [ANDROID APP]
  (Đầu ra chính - Kính)     (Thiết bị đồng hành - Tùy chọn)
```

### 2. Thông Số Phần Cứng
| Linh kiện | Vai trò | Đặc tả kỹ thuật |
| :--- | :--- | :--- |
| **Raspberry Pi 4 Model B** | Bộ não trung tâm On-Device Edge AI | RAM 8GB / 4GB, CPU Broadcom BCM2711 Quad-core Cortex-A72 @ 1.5GHz |
| **Camera Module (OV5647)** | Mắt cảm biến thu nhận cử chỉ | Độ phân giải 5MP, giao tiếp cổng CSI chuyên dụng, góc siêu rộng (FOV 120°) |
| **Loa Tích Hợp (Mini Speaker)** | Đầu ra âm thanh chính (ADR-004) | Kết nối qua cổng 3.5mm / I2S / Bluetooth, phát âm thanh giọng đọc tiếng Việt |
| **Gọng Kính Thông Minh** | Khung gắn phần cứng | Khung in 3D nhẹ, camera đặt chính giữa hoặc gọng bên, vi mạch Pi đeo thắt lưng/túi |
| **Nguồn Cấp Di Động** | Cung cấp năng lượng | Pin sạc dự phòng chuẩn 5V - 3A (USB-C) |

---

## 📁 Cấu Trúc Thư Mục Dự Án

```text
do_an_tot_nghiep/
├── src/                               # Toàn bộ mã nguồn thực thi
│   ├── preprocess.py                  # Trích xuất 48 landmark từ video MP4 ra mảng Numpy (.npy)
│   ├── data_loader.py                 # Nạp dữ liệu, chuẩn hóa đặc trưng và tạo tf.data Pipeline
│   ├── model.py                       # Định nghĩa mạng BiGRU Attention và GRU Baseline
│   ├── split_data.py                  # Phân chia dữ liệu train/test theo tỷ lệ chuẩn
│   ├── export_tflite.py               # Chuyển đổi mô hình Keras sang TensorFlow Lite FP32
│   ├── export_tflite_quant.py         # Lượng tử hóa mô hình sang TFLite Dynamic Range (1.2 MB)
│   ├── inference_webcam.py            # Chương trình nhận diện trực tiếp qua Webcam PC / Laptop
│   ├── inference_pi_tflite.py         # Pipeline nhận diện chính thức trên Raspberry Pi qua TFLite
│   ├── inference_video.py             # Script kiểm thử độ chính xác trên video có sẵn
│   └── model_loader.py                # Tiện ích nạp trọng số và tương thích mô hình
├── models/                            # Thư mục lưu trữ trọng số mô hình
│   ├── vsl_bigru_attention_dynamic.tflite # Mô hình TFLite lượng tử hóa siêu nhẹ (1.20 MB) - Cho Pi
│   ├── vsl_bigru_attention.tflite     # Mô hình TFLite FP32 (4.46 MB)
│   ├── vsl_gru_baseline.h5            # Trọng số baseline GRU
│   └── classes.json                   # Từ điển mapping 473 nhãn từ vựng tiếng Việt (Nguồn chuẩn duy nhất)
├── data/                              # Dữ liệu phục vụ huấn luyện và kiểm thử
│   ├── keypoints_splited/             # Tập keypoints train/test đã phân chia
│   └── my_preprocessed/               # Dữ liệu đặc trưng trích xuất tạm thời
├── docs/                              # Tài liệu kỹ thuật chi tiết đồ án
│   ├── 00_Project/                    # Tổng quan, yêu cầu và roadmap
│   ├── 01_System/                     # Kiến trúc hệ thống và luồng dữ liệu
│   ├── 02_RaspberryPi/                # Pipeline camera, MediaPipe và TFLite trên Pi
│   ├── 03_AI/                         # Bộ dữ liệu, tiền xử lý và huấn luyện
│   ├── 04_Android/                    # Thiết kế ứng dụng đồng hành Companion App
│   ├── 05_API/                        # Đặc tả giao thức WebSocket và REST API
│   ├── 08_Agents/                     # Nhật ký quản lý công việc và Task Cards
│   └── 99_Decisions/                  # Các quyết định kiến trúc cốt lõi (ADR-001 -> ADR-004)
├── chay_test_cam.bat                  # File tiện ích click chạy nhanh kiểm thử webcam trên Windows
├── TONG_QUAN_DO_AN.md                 # Báo cáo tổng quan đồ án chi tiết
├── PROJECT_BRIEF_DAY_DU.md            # Bản tóm tắt nhiệm vụ đề tài đầy đủ
└── README.md                          # Tài liệu giới thiệu dự án
```

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Thử Nghiệm

### 1. Môi Trường Yêu Cầu
* **Hệ điều hành:** Windows 10/11 (Development/Testing) hoặc Raspberry Pi OS 64-bit (Deployment).
* **Phiên bản Python:** Python 3.9 - 3.11.

### 2. Cài Đặt Thư Viện Cần Thiết

```bash
# Tạo và kích hoạt môi trường ảo (Khuyến nghị)
python -m venv .venv

# Trên Windows:
.\.venv\Scripts\activate
# Trên Linux / Raspberry Pi:
source .venv/bin/activate

# Cài đặt các gói phụ thuộc
pip install --upgrade pip
pip install mediapipe==0.10.14
pip install opencv-python numpy pyttsx3

# Môi trường PC (Huấn luyện & Chạy kiểm thử đầy đủ):
pip install tensorflow

# Môi trường Raspberry Pi (Tối ưu tài nguyên, chỉ chạy inference):
# pip install tflite-runtime (hoặc dùng tensorflow-lite nếu tương thích)
```

---

### 3. Kịch Bản 1: Thử Nghiệm Trực Tiếp Trên PC Bằng Webcam

Để kiểm thử nhanh khả năng nhận diện ký hiệu, tích lũy từ và ghép câu tiếng Việt qua webcam máy tính:

* **Cách 1 (Nhanh nhất trên Windows):** Click đúp chuột vào file `chay_test_cam.bat`.
* **Cách 2 (Dòng lệnh PowerShell / CMD):**
  ```powershell
  python src/inference_webcam.py --model models/vsl_bigru_attention_dynamic.tflite --conf 0.10 --margin 0.02
  ```

#### 🎮 Bảng Phím Tắt Điều Khiển Khi Chạy Webcam:
| Phím nóng | Chức năng |
| :---: | :--- |
| **`C`** / **`c`** | **Xóa câu:** Xóa toàn bộ chuỗi câu đang tích lũy trên màn hình. |
| **`[`** | **Giảm ngưỡng tin cậy:** Giảm `conf_threshold` từng bước 0.02 để dễ nhận diện từ hơn. |
| **`]`** | **Tăng ngưỡng tin cậy:** Tăng `conf_threshold` từng bước 0.02 để lọc chặt chẽ hơn. |
| **`F`** / **`f`** | **Chuyển chế độ lật Camera:** Chuyển đổi giữa chế độ chuẩn AI (No-flip) và chế độ gương (Flip). |
| **`Q`** / **`q`** | **Thoát:** Đóng cửa sổ ứng dụng và giải phóng camera. |

---

### 4. Kịch Bản 2: Chạy Suy Luận Chính Thức Trên Raspberry Pi (Edge AI)

Trên bo mạch Raspberry Pi kết nối với Camera CSI OV5647 và Loa:

```bash
# Chạy chương trình nhận diện TFLite thời gian thực kèm phát âm thanh Offline TTS
python src/inference_pi_tflite.py --model models/vsl_bigru_attention_dynamic.tflite

# Chạy ở chế độ không phát loa (nếu đang debug không có loa cắm):
python src/inference_pi_tflite.py --model models/vsl_bigru_attention_dynamic.tflite --no_tts
```

---

### 5. Kịch Bản 3: Quy Trình Tiền Xử Lý & Huấn Luyện Lại Mô Hình (Training Pipeline)

1. **Trích xuất đặc trưng 48 điểm từ video:**
   ```bash
   python src/preprocess.py
   ```
2. **Chia tập dữ liệu Train / Test:**
   ```bash
   python src/split_data.py
   ```
3. **Huấn luyện mô hình BiGRU Attention:**
   ```bash
   python src/model.py
   ```
4. **Xuất mô hình tối ưu sang định dạng TFLite:**
   ```bash
   python src/export_tflite_quant.py
   ```

---

## 📊 Bảng Trạng Thái Tính Năng (Status Taxonomy)

Theo quy chuẩn tài liệu của dự án, các tính năng được phân loại theo 3 trạng thái:
* **`Implemented`**: Đã hoàn thiện mã nguồn, kiểm thử thành công và có bằng chứng trong repo.
* **`Need Verification`**: Đã có mã nguồn sơ bộ nhưng cần kiểm chứng thực nghiệm trên phần cứng thực tế.
* **`Planned`**: Thiết kế kiến trúc đã hoàn thiện, sẵn sàng cho giai đoạn phát triển tiếp theo.

| Hạng mục | Tính năng / Thành phần | Trạng thái | Ghi chú |
| :--- | :--- | :---: | :--- |
| **Edge AI Pipeline** | Trích xuất 48 landmark 3D với MediaPipe Holistic | **Implemented** | 42 điểm tay + 6 điểm thân trên (144 features) |
| | Chuẩn hóa tọa độ bất biến vị trí & khoảng cách | **Implemented** | Tịnh tiến theo trung điểm vai, scale theo khoảng cách vai |
| | Mô hình BiGRU Attention nhận diện 473 từ VSL | **Implemented** | Kiểm thử đạt accuracy cao trên tập dữ liệu |
| | Nén & Lượng tử hóa TFLite Dynamic Range (1.2 MB) | **Implemented** | `models/vsl_bigru_attention_dynamic.tflite` |
| | Máy trạng thái 4 pha & Ghép câu thời gian thực | **Implemented** | Hỗ trợ Debounce, Confidence filter, xóa câu |
| **Phần cứng Kính** | Camera góc rộng 120° CSI OV5647 | **Need Verification** | Đã test trên Webcam PC; chờ nghiệm thu trên khung kính |
| | Kính không có màn hình (ADR-004) | **Implemented** | Loại bỏ HUD để giảm nhiệt, điện năng và khối lượng |
| | Đầu ra giọng nói qua Loa tích hợp (Offline TTS) | **Implemented** | Tích hợp engine `pyttsx3` trong `inference_pi_tflite.py` |
| **Companion App** | Giao diện Android Jetpack Compose hiển thị phụ đề | **Planned** | Thiết kế hoàn tất (docs/04_Android), chờ triển khai source code |
| | Đồng bộ dữ liệu qua WebSocket nội bộ không Internet | **Planned** | Kết nối mạng cục bộ do Pi phát Hotspot |

---

## 📜 Các Quyết Định Kiến Trúc Trọng Tâm (ADRs)

Dự án tuân thủ nghiêm ngặt các Quyết định Kiến trúc đã được phê duyệt:
* [**ADR-001: Raspberry Pi là Trung tâm Edge AI Độc lập**](docs/99_Decisions/ADR-001.md) — Toàn bộ pipeline nhận diện và phát âm thanh chạy offline 100% trên Pi. Android chỉ là thiết bị đồng hành tùy chọn.
* [**ADR-002: Pipeline MediaPipe Landmark + GRU + TFLite**](docs/99_Decisions/ADR-002.md) — Sử dụng 48 điểm đặc trưng cốt lõi và mạng nơ-ron chuỗi siêu nhẹ thay vì đưa khung hình ảnh thô trực tiếp vào mô hình nặng.
* [**ADR-003: Cấu trúc Giao thức Giao tiếp WebSocket & Schema Dữ liệu**](docs/99_Decisions/ADR-003.md) — Định nghĩa gói tin JSON chuẩn giữa Pi và Android App.
* [**ADR-004: Kính Không Có Màn Hình, Đầu Ra Chính Là Âm Thanh**](docs/99_Decisions/ADR-004.md) — Loại bỏ màn hình gắn kính; dùng Offline TTS phát qua loa tích hợp để giải phóng thị giác cho người đeo kính.

---

## 👥 Nhóm Tác Giả & Bản Quyền

* **Đề tài:** Đồ án Tốt nghiệp Kỹ sư / Cử nhân Công nghệ Thông tin
* **Đơn vị:** Khoa Công nghệ Thông tin
* **Giấy phép (License):** Mã nguồn được phát triển phục vụ mục đích nghiên cứu và giáo dục phi thương mại.
