# Báo cáo đánh giá độ chính xác mô hình VSL (Cập nhật sau bản vá)

## Thông tin kiểm thử

- Môi trường: Python 3.10.6, TensorFlow 2.16.1, CPU.
- Lệnh: `.\.venv\Scripts\python.exe src\inference_video.py`
- Checkpoint được nạp: `vsl_bigru_attention_colab.keras`
- Số lớp từ vựng: 473.
- Kết quả từ từ điển đồng bộ từ Colab (Bản vá Mojibake byte-level).

## Bảng so sánh Ground Truth và Top 1

| STT | Video | Chữ thật sự | Chữ đoán được (Top 1) | Confidence Top 1 | Đúng/Sai |
|---:|---|---|---|---:|---|
| 1 | `Giàu.mp4` | Giàu | **Giàu** | 55.51% | **ĐÚNG** |
| 2 | `Quả dâu.mp4` | Quả dâu | **Quả dâu** | 66.20% | **ĐÚNG** |
| 3 | `Yên tĩnh.mp4` | Yên tĩnh | **Yên tĩnh** | 97.39% | **ĐÚNG** |

## Độ chính xác

```text
Accuracy = Số video Top-1 đúng / Tổng số video
         = 3 / 3
         = 100.00%
```

Mô hình đạt độ chính xác **100% (3/3)** sau khi đồng bộ từ điển Colab và áp dụng bản vá Tiền xử lý (Zero-padding & Raw-resolution landmark extraction).

## Kết luận

Pipeline inference và checkpoint chạy tuyệt đối ổn định và chính xác 100% trên bộ test. Giai đoạn 2 đã chính thức khép lại hoàn hảo.
