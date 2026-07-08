# HƯỚNG DẪN SỬ DỤNG GITHUB DÀNH CHO TEAM ĐỒ ÁN

Tài liệu này là "cẩm nang sinh tồn" giúp team 2 người của bạn làm việc chung mượt mà, không bao giờ lo mất code hay bị đè file của nhau. Hãy đọc kỹ phần **"Quy trình hằng ngày"** và **"Xử lý xung đột"**.

---

## 1. Tư duy cốt lõi (Git và GitHub là gì?)
*   **Git (Local):** Là phần mềm cài trong máy tính của bạn. Nó đóng vai trò như một "nhà kho" ghi chép lại mọi sự thay đổi bạn làm (thêm dòng code, xóa file...).
*   **GitHub (Remote):** Là một trang web (đám mây). Nó là một "nhà kho tổng". Nhiệm vụ của bạn là lấy code từ máy tính (Git) ném lên đám mây (GitHub) để người khác tải về.

## 2. QUY TRÌNH HẰNG NGÀY (BẮT BUỘC NHỚ)

Để tránh mọi lỗi thảm họa, mỗi khi ngồi vào bàn làm việc, bạn phải tuân thủ đúng thứ tự 4 bước sau:

### Bước 1: Kéo code mới nhất về máy (`git pull`)
*   **Lúc nào cần:** NGAY KHI MỞ MÁY LÊN.
*   **Lệnh:** `git pull`
*   **Lý do:** Tối qua bạn của bạn có thể đã sửa code và đẩy lên GitHub. Nếu bạn không kéo về mà cứ thế sửa tiếp code cũ trong máy mình, lát nữa đẩy lên sẽ bị lỗi "đụng độ" (Conflict).

### Bước 2: Code và Lưu file (`Ctrl + S`)
*   Thoải mái mở VS Code, Pycharm, Word... sửa file và bấm Save bình thường.

### Bước 3: Gói hàng và Dán nhãn (`git add` & `git commit`)
*   **Lúc nào cần:** Sau khi làm xong một chức năng (ví dụ: viết xong phần Tiền xử lý), hoặc trước khi tắt máy tính đi ngủ.
*   **Lệnh 1 (Gom hàng):** 
    `git add .` *(Dấu chấm là gom tất cả các file vừa sửa. Các file nặng như video đã bị `.gitignore` chặn nên cứ yên tâm).*
*   **Lệnh 2 (Dán nhãn ghi chú):** 
    `git commit -m "Sua loi thuật toan trich xuat 48 diem"` *(Nhớ ghi chú tiếng Việt có dấu hay không dấu đều được, nhưng phải rõ ràng).*

### Bước 4: Đẩy lên mạng (`git push`)
*   **Lúc nào cần:** Ngay sau Bước 3.
*   **Lệnh:** `git push`
*   **Kết quả:** Code của bạn bay lên mây, và bây giờ bạn của bạn có thể dùng `git pull` để lấy đống code đó về.

---

## 3. CÁC TÌNH HUỐNG THƯỜNG GẶP VÀ CÁCH CỨU NẠN

### Tình huống A: Quên `git pull` ở đầu ngày, đến cuối ngày gõ `git push` thì bị báo LỖI ĐỎ.
*   **Giải thích:** Bạn và bạn của bạn **cùng sửa chung 1 file** (ví dụ file `model.py`). GitHub không biết nên lấy bản của ai và bỏ bản của ai, nên nó cấm bạn đẩy lên. Hiện tượng này gọi là **Conflict (Xung đột)**.
*   **Cách cứu:**
    1. Vẫn gõ lệnh kéo về: `git pull`
    2. Mở VS Code lên, vào file `model.py`. Bạn sẽ thấy VS Code bôi màu xanh đỏ cực kỳ lạ mắt (hiển thị code của bạn và code của bạn kia). 
    3. VS Code sẽ hiện các nút bấm: `Accept Current Change` (Lấy code của bạn), `Accept Incoming Change` (Lấy code của bạn kia), hoặc `Accept Both Changes` (Lấy cả hai). Bấm chọn 1 cái.
    4. Bấm `Ctrl + S` lưu file lại.
    5. Gõ lại vòng tuần hoàn: `git add .` -> `git commit -m "Giai quyet conflict"` -> `git push`.

### Tình huống B: Code bị hỏng nặng, muốn QUAY LẠI phiên bản hôm qua.
*   **Cảnh báo:** Phải cẩn thận khi dùng tính năng này.
*   **Cách làm:**
    1. Mở Terminal gõ: `git log` (Nó sẽ hiện ra danh sách các lần `commit` bạn từng dán nhãn, kèm theo một mã số dài ngoằng màu vàng, ví dụ `930e757...`).
    2. Bạn thấy bản commit có ghi chú "Code ngon lành nhất" mã là `abc1234`. Nhấn phím `Q` để thoát danh sách.
    3. Gõ lệnh: `git reset --hard abc1234`
    4. BÙM! Toàn bộ thư mục code của bạn sẽ lập tức "xuyên không" biến về y hệt trạng thái lúc bạn commit `abc1234`.

---

## 4. Tóm tắt nhanh các lệnh thường dùng

| Lệnh | Ý nghĩa dân dã |
| :--- | :--- |
| `git status` | Khám xét xem mình đã sửa những file nào từ sáng đến giờ. |
| `git add .` | Gom mọi thứ vừa sửa vào hộp. |
| `git commit -m "abc"`| Dán nhãn lên hộp ghi rõ "abc". |
| `git push` | Bốc hộp quăng lên xe tải gửi lên GitHub. |
| `git pull` | Lên GitHub lấy hộp của người khác tải về máy mình. |
| `git log` | Xem cuốn sổ nhật ký xem ai vừa gửi hộp gì lên lúc mấy giờ. |
