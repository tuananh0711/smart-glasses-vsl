# BÁO CÁO KIỂM THỬ CAMERA & GUI (QC)

## Kết luận

**PASS** — Không phát hiện lỗi vận hành camera, GUI OpenCV hoặc đóng băng luồng MediaPipe trong môi trường kiểm thử hiện tại. Không sửa đổi `src/inference_webcam.py`.

## Môi trường và phạm vi

- Dự án: `D:\do_an_tot_nghiep`
- Trình thông dịch: `.venv\Scripts\python.exe` (Python 3.10)
- Script: `src\inference_webcam.py`
- Camera backend được kiểm tra: `cv2.CAP_DSHOW`, thiết bị index `0`
- Cửa sổ mục tiêu: `TEST AI KINH THONG MINH`

## Kết quả kiểm thử

| Hạng mục | Kết quả | Bằng chứng |
|---|---|---|
| Khởi chạy script đầy đủ | PASS | Script tải checkpoint `vsl_bigru_attention_colab.keras`, khởi tạo TensorFlow/MediaPipe và đi vào luồng camera. Cảnh báo optimizer của Keras không ảnh hưởng suy luận. |
| Mở camera DirectShow | PASS | Phép thử độc lập trả về `OPENED=True`. |
| Đọc frame đầu tiên | PASS | `FIRST_READ=True`, frame nhận được không phải `None`. |
| Hiển thị GUI OpenCV | PASS | Windows API phát hiện cửa sổ hiển thị thuộc tiến trình Python với tiêu đề chính xác `TEST AI KINH THONG MINH`; phép thử GUI tối giản trả `VISIBLE=1.0`. |
| Vòng lặp `cv2.waitKey` | PASS | Phép thử GUI xử lý 292 frame trong 10,04 giây và cửa sổ vẫn phản hồi. |
| MediaPipe có freeze ở frame đầu | PASS (không freeze) | Hai ảnh chụp nội dung cửa sổ cách nhau 2 giây có `MEAN_ABS_DIFF=17.3391` và `CHANGED_PIXEL_RATIO=0.893305`; nội dung video tiếp tục cập nhật rõ rệt. |
| Giải phóng thiết bị sau kiểm thử | PASS | Tiến trình kiểm thử được dừng có kiểm soát sau khi thu thập bằng chứng; camera không còn bị phiên kiểm thử chiếm dụng. |

## Đánh giá nguyên nhân sự cố tiềm năng

Trong lần chạy hợp lệ, không xuất hiện xung đột MSMF/DirectShow, không có bằng chứng camera bị ứng dụng khác chiếm dụng, và vòng lặp GUI không bị lỗi `waitKey`. Một lần quan sát ban đầu không thấy cửa sổ là do hai tiến trình kiểm thử chạy chồng lấn và tranh chấp camera; sau khi dừng phiên cũ và chạy lại độc lập, DirectShow, GUI và MediaPipe đều hoạt động bình thường.

## Nhận xét mã nguồn

Luồng hiện tại sử dụng `cv2.VideoCapture(0, cv2.CAP_DSHOW)`, gọi `cv2.imshow` và `cv2.waitKey(10)` trong mỗi vòng lặp, sau đó `cap.release()` và `cv2.destroyAllWindows()`. Vì nghiệm thu thực tế đạt yêu cầu, không thực hiện bản vá ngoài phạm vi.
