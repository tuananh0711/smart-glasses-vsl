# Lưu trữ kết quả đợt làm việc: test_1

- **Thời điểm đóng gói**: 25/09/2026
- **Mục đích**: Lưu trữ toàn bộ mã nguồn, mô hình, video mẫu, notebook training và logs của đợt thử nghiệm đầu tiên (test_1) để chuẩn bị tái cấu trúc và làm lại quy trình chuẩn chỉnh hơn.

## Thành phần được đóng gói:
1. `src/`: Toàn bộ mã nguồn xử lý pipeline, inference webcam, segmentation, tflite.
2. `models/`: Các file mô hình trọng số (`.h5`, `.keras`, `.tflite`) và file `classes.json`.
3. `logs/`: TensorBoard logs và logs tiền xử lý dữ liệu.
4. `test_videos/`: 10 video clips mẫu test offline + `README.txt`.
5. `Train_Colab.ipynb` & `make_colab_nb.py`: Notebook và script khởi tạo training Colab của đợt 1.
6. Báo cáo & Logs chạy webcam:
   - `webcam_test_report.md`
   - `accuracy_report.md`
   - `qc_report.md`
   - `agent_for_kilo.md`
   - `webcam_*.log`
   - Scripts hỗ trợ: `run_webcam.bat`, `chay_test_cam.bat`, `inspect_model.py`, `extract_weights.py`.
