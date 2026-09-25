# Quy tắc 1: Bàn giao Kiểm thử Kilo Code Bên ngoài (External Kilo Code Handoff)

Khi một task có liên quan đến việc lập trình, sửa code hoặc viết tài liệu, hãy tuân thủ quy trình sau cho giai đoạn kiểm thử cuối cùng:

1. **Kiểm thử Nội bộ Trước (Internal QC First)**: Đảm bảo công việc đã vượt qua sự kiểm tra của subagent `QC-1` nội bộ trước.
2. **Tạo file agent_for_kilo.md**: Sau khi vượt qua QC-1 nội bộ, LUÔN LUÔN ghi hướng dẫn bàn giao vào file `D:\do_an_tot_nghiep\agent_for_kilo.md`.
3. **Yêu cầu đối với agent_for_kilo.md**: File BẮT BUỘC phải chứa:
   - Danh sách các file cụ thể vừa được chỉnh sửa.
   - Tóm tắt ngắn gọn nội dung đã thay đổi và mục tiêu.
   - Hướng dẫn rõ ràng để Kilo Code bên ngoài:
     - Kiểm tra các file đã sửa để tìm lỗi logic, lỗ hổng bảo mật, các trường hợp biên (edge cases) và lỗi định dạng.
     - Đánh giá độc lập mà không tin tưởng tuyệt đối vào kết quả pass của QC-1.
     - Ghi kết quả đánh giá vào file `qc_report.md`.
     - Nếu FAIL: Ghi rõ file lỗi, loại lỗi, lý do và cách khắc phục.
     - Nếu PASS: Chỉ cần ghi "PASS" vào `qc_report.md`.
4. **Tự động kích hoạt Kilo Code (Automated Kilo Trigger)**: Antigravity tự động kích hoạt Kilo CLI chạy ngầm (`kilo.exe run`) để đọc `agent_for_kilo.md`, tiến hành thẩm định và ghi kết quả vào `qc_report.md`.
5. **Đánh giá và Báo cáo (1 Chu kỳ khép kín)**: Khi Kilo hoàn tất, Antigravity tự động đọc `qc_report.md`, trích xuất kết quả đánh giá của Kilo, đưa ra phương án xử lý và báo cáo tổng kết đầy đủ cho Người dùng. Chu kỳ dừng lại tại đây để Người dùng xem xét (giới hạn đúng 1 chu kỳ, tránh vòng lặp vô tận).

# Quy tắc 2: Ranh giới Kiến trúc Edge AI (Edge AI Boundary)

- **Raspberry Pi là Trung tâm Edge AI**: Toàn bộ pipeline MediaPipe landmark extraction, normalization, GRU/TFLite inference, và Sentence Builder chạy offline 100% trên Raspberry Pi (ADR-001).
- **Kính KHÔNG CÓ MÀN HÌNH**: Kính không gắn màn hình hiển thị (ADR-004). Đầu ra chính của hệ thống là offline Text-to-Speech (TTS) phát trực tiếp qua loa trên kính.
- **Android là App Phụ trợ (Companion App)**: Android chỉ nhận kết quả dịch qua WebSocket/REST API để hiển thị văn bản, xem lịch sử và quản lý cài đặt. Không đưa MediaPipe, TensorFlow hay TFLite mô hình dịch sang Android.
- **Tính Độc lập**: Raspberry Pi phải hoạt động bình thường ngay cả khi mất kết nối Android, Wi-Fi hoặc Internet.

# Quy tắc 3: Quản lý Task & Ranh giới Phạm vi (Task Cards & Scope Control)

Khi thực thi bất kỳ giai đoạn lập trình hoặc cập nhật nào:
1. **Tuân thủ Task Card**: Tham chiếu hoặc tạo task trong `docs/08_Agents/tasks/` theo `TASK_TEMPLATE.md`.
2. **Khoanh vùng File**:
   - `Allowed scope`: Chỉ chỉnh sửa đúng các file được phép trong task card.
   - `Forbidden scope`: Tuyệt đối không chỉnh sửa các file thuộc phạm vi cấm.
3. **Tiêu chuẩn Hoàn thành & Kiểm thử (Acceptance Criteria & Verification)**:
   - Mọi task phải ghi rõ điều kiện nghiệm thu (Acceptance Criteria).
   - Bắt buộc thực thi câu lệnh kiểm thử tự động (Verification commands như `pytest`, `./gradlew assembleDebug test`) và lưu bằng chứng kết quả trước khi bàn giao.

# Quy tắc 4: Quy ước Trạng thái (Status Taxonomy)

Mọi báo cáo, tài liệu và task card phải sử dụng 3 trạng thái chuẩn:
- **`Planned`**: Chức năng/thiết kế đã có trong tài liệu nhưng chưa có source code hoặc cấu hình thực tế trong repository.
- **`Implemented`**: Đã có source code hoàn chỉnh, chạy build/test thành công và có bằng chứng kiểm thử trong repository.
- **`Need Verification`**: Đã có source code nhưng chưa đủ bằng chứng kiểm thử tự động hoặc chưa xác nhận phần chứng/BOM.
