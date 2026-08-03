========================================================================
 HƯỚNG DẪN THỬ NGHIỆM DỊCH VIDEO KÝ HIỆU (OFFLINE AI TEST)
========================================================================

1. THẢ VIDEO CLIP VÀO ĐÂY:
   - Thả các tệp video clip (.mp4, .avi, .mov, .mkv) của bạn vào thư mục:
     D:\do_an_tot_nghiep\test_videos\input_videos\

2. CÁCH KHỞI CHẠY LỆNH TEST VIDEO:
   - Mở Terminal trong VS Code / PowerShell và chạy câu lệnh:
     .\.venv\Scripts\python.exe src/inference_video.py

3. CÁC NÚT ĐIỀU KHIỂN KHI VIDEO ĐANG PHÁT:
   - Phím [SPACE] (Khoảng trắng): Tạm dừng / Xem tiếp video
   - Phím [n]: Chuyển sang clip video tiếp theo
   - Phím [q]: Thoát chương trình

4. TÍNH NĂNG HIỂN THỊ TRÊN MÀN HÌNH:
   - Tên tệp video đang phát.
   - 48 điểm đặc trưng chuẩn hóa (21 điểm tay trái, 21 điểm tay phải, 6 điểm vai/khuỷu/cổ tay).
   - Từ vựng AI đang dự đoán thời gian thực + % độ tin cậy.
   - Chuỗi câu tiếng Việt dịch được ghép đầy đủ dấu sắc nét.
========================================================================
