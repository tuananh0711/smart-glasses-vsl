import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import json
import sys
import glob
from PIL import ImageFont, ImageDraw, Image
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from model import build_gru_model, build_bigru_attention_model

def draw_vietnamese_text(img, text, position, font_size=32, color=(0, 255, 0)):
    """Vẽ chữ tiếng Việt có dấu chuẩn đẹp trên khung hình OpenCV bằng PIL"""
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        try:
            font = ImageFont.truetype("segoeui.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()
            
    x, y = position
    draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=(color[2], color[1], color[0]))
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

def pad_or_truncate(data, max_frames=60):
    """Đệm mảng 0 hoặc cắt ngắn dữ liệu về đúng 60 frames"""
    t = data.shape[0]
    if t >= max_frames:
        return data[:max_frames]
    else:
        pad_size = max_frames - t
        padding = np.zeros((pad_size, 48, 3), dtype=np.float32)
        return np.vstack([data, padding])

# Cấu hình đường dẫn
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH_H5 = os.path.join(_BASE_DIR, 'models', 'vsl_gru_baseline.h5')
CLASSES_PATH = os.path.join(_BASE_DIR, 'models', 'classes.json')
TEST_VIDEOS_DIR = os.path.join(_BASE_DIR, 'test_videos', 'input_videos')

MAX_FRAMES = 60
NUM_POINTS = 48
NUM_DIMS = 3
WINDOW_NAME = "DEMO TEST DỊCH VIDEO KÝ HIỆU AI"

mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

def extract_keypoints_48(results):
    """Trích xuất và chuẩn hóa 48 điểm đặc trưng"""
    pose = np.zeros((6, 3))
    center_x, center_y, center_z = 0.5, 0.5, 0.0
    scale = 1.0
    
    if results.pose_landmarks:
        for i, idx in enumerate([11, 12, 13, 14, 15, 16]):
            res = results.pose_landmarks.landmark[idx]
            vis = getattr(res, 'visibility', 1.0)
            if vis > 0.5:
                pose[i] = [res.x, res.y, res.z]
            else:
                pose[i] = [0.0, 0.0, 0.0]
                
        if not np.array_equal(pose[0], [0.0, 0.0, 0.0]) and not np.array_equal(pose[1], [0.0, 0.0, 0.0]):
            center_x = (pose[0][0] + pose[1][0]) / 2
            center_y = (pose[0][1] + pose[1][1]) / 2
            center_z = (pose[0][2] + pose[1][2]) / 2
            
            dist = np.linalg.norm(pose[0] - pose[1])
            if dist > 0.01:
                scale = dist

    lh = np.zeros((21, 3))
    if results.left_hand_landmarks:
        for i, res in enumerate(results.left_hand_landmarks.landmark):
            lh[i] = [res.x, res.y, res.z]
            
    rh = np.zeros((21, 3))
    if results.right_hand_landmarks:
        for i, res in enumerate(results.right_hand_landmarks.landmark):
            rh[i] = [res.x, res.y, res.z]
            
    keypoints = np.vstack([pose, lh, rh])
    
    for i in range(len(keypoints)):
        if not np.array_equal(keypoints[i], [0.0, 0.0, 0.0]):
            keypoints[i][0] = (keypoints[i][0] - center_x) / scale
            keypoints[i][1] = (keypoints[i][1] - center_y) / scale
            keypoints[i][2] = (keypoints[i][2] - center_z) / scale

    return keypoints

def process_single_video(video_path, model, class_names):
    """Xử lý và hiển thị quá trình nhận diện cho 1 tệp video"""
    video_name = os.path.basename(video_path)
    print(f"\n🎬 Đang phát video thử nghiệm: {video_name}")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Không thể mở video: {video_path}")
        cap.release()
        return True

    try:
        # 1. Lấy tổng số frame từ metadata (hoặc chạy đếm nhanh nếu metadata không hợp lệ)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not np.isfinite(fps) or fps <= 0:
            fps = 30.0
        delay_ms = max(1, int(round(1000.0 / fps)))

        if total_frames <= 0:
            total_frames = 0
            while cap.isOpened():
                ret, _ = cap.read()
                if not ret:
                    break
                total_frames += 1
            cap.release()
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"❌ Không thể mở lại video ở Pass 2: {video_path}")
                cap.release()
                return True

        if total_frames <= 0:
            print(f"⚠️ Video rỗng hoặc không đọc được khung hình: {video_name}")
            return True

        # 2. Lập mảng target_indices (60 chỉ số) và set các khung hình độc nhất (O(1) bộ nhớ)
        target_indices = np.linspace(0, total_frames - 1, MAX_FRAMES, dtype=int)
        target_set = set(target_indices)

        keypoints_by_idx = {}
        raw_annotated_image = None
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # 1. TRÍCH XUẤT ĐẶC TRƯNG TRÊN FRAME GỐC (Khớp 100% với preprocess.py lúc train)
            raw_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            raw_rgb.flags.writeable = False
            results = holistic.process(raw_rgb)
            
            # Chỉ lưu điểm vào dict theo index nếu frame_idx thuộc target_set
            if frame_idx in target_set:
                keypoints_by_idx[frame_idx] = extract_keypoints_48(results)

            # 2. PHÓNG TO FRAME ĐỂ HIỂN THỊ GIAO DIỆN MƯỢT MÀ
            h_raw, w_raw, _ = frame.shape
            if h_raw < 720:
                target_h = 720
                target_w = int(w_raw * (target_h / h_raw))
                image = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
            else:
                image = frame.copy()

            # 1. Vẽ 21 điểm tay trái + 21 điểm tay phải
            if results.left_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=(240, 240, 240), thickness=2)
                )
            if results.right_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=(240, 240, 240), thickness=2)
                )
            
            # 2. Vẽ 6 điểm Pose
            if results.pose_landmarks:
                h, w, _ = image.shape
                pose_indices = [11, 12, 13, 14, 15, 16]
                pts = {}
                for idx in pose_indices:
                    lm = results.pose_landmarks.landmark[idx]
                    vis = getattr(lm, 'visibility', 1.0)
                    if vis > 0.5:
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        pts[idx] = (cx, cy)
                        cv2.circle(image, (cx, cy), 6, (0, 255, 255), -1)
                        cv2.circle(image, (cx, cy), 8, (0, 0, 255), 2)

                pose_connections = [(11, 12), (11, 13), (13, 15), (12, 14), (14, 16)]
                for p1, p2 in pose_connections:
                    if p1 in pts and p2 in pts:
                        cv2.line(image, pts[p1], pts[p2], (0, 255, 255), 3)

            # Dựng sequence dự đoán từ các mảng duy nhất đã thu thập, sau đó pad zeros giống preprocess.py
            cur_seq = [keypoints_by_idx[i] for i in sorted(keypoints_by_idx.keys())]

            top_rt1 = "Đang phân tích..."
            top_rt2 = ""
            top_rt3 = ""

            if len(cur_seq) >= 5:
                seq_padded = pad_or_truncate(np.array(cur_seq), MAX_FRAMES)
                input_data = np.expand_dims(seq_padded, axis=0)
                input_data = np.reshape(input_data, (1, MAX_FRAMES, NUM_POINTS * NUM_DIMS))
                
                res = model.predict(input_data, verbose=0)[0]
                top_idxs = np.argsort(res)[-3:][::-1]
                
                w1, c1 = class_names[top_idxs[0]], res[top_idxs[0]] * 100
                w2, c2 = class_names[top_idxs[1]], res[top_idxs[1]] * 100
                w3, c3 = class_names[top_idxs[2]], res[top_idxs[2]] * 100

                top_rt1 = f"[{w1}] ({c1:.1f}%)"
                top_rt2 = f"2. {w2} ({c2:.1f}%)"
                top_rt3 = f"3. {w3} ({c3:.1f}%)"

            # Lưu ảnh đã vẽ 48 điểm nhưng CHƯA vẽ chữ để dùng cho màn hình kết quả dừng lại
            raw_annotated_image = image.copy()

            # Hiển thị thông tin thời gian thực trong lúc đang phát video (Top 3)
            image = draw_vietnamese_text(image, f"Video: {video_name}", (20, 15), font_size=26, color=(255, 255, 255))
            image = draw_vietnamese_text(image, f"Dự đoán 1: {top_rt1}", (20, 55), font_size=32, color=(0, 255, 255))
            if top_rt2:
                image = draw_vietnamese_text(image, f"Gợi ý khác: {top_rt2}  |  {top_rt3}", (20, 105), font_size=24, color=(200, 200, 200))

            cv2.imshow(WINDOW_NAME, image)

            key = cv2.waitKey(delay_ms) & 0xFF

            # Kiểm tra xem người dùng có đóng cửa sổ bằng nút X hay không (NGAY SAU waitKey)
            if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                print("🛑 Cửa sổ đã bị đóng bởi người dùng.")
                return False

            if key == ord('q'):
                print("🛑 Đã ngắt phát video.")
                return False
            elif key == ord('n'):
                print("⏩ Nhảy sang video tiếp theo.")
                return True

            frame_idx += 1

        # Đảm bảo padding bằng ZEROS giống lúc train, không lặp frame (Duplication)
        final_seq = [keypoints_by_idx[i] for i in sorted(keypoints_by_idx.keys())]
        if len(final_seq) > 0:
            seq_padded = pad_or_truncate(np.array(final_seq), MAX_FRAMES)
            input_data = np.expand_dims(seq_padded, axis=0)
            input_data = np.reshape(input_data, (1, MAX_FRAMES, NUM_POINTS * NUM_DIMS))
            
            res = model.predict(input_data, verbose=0)[0]
            top_indices = np.argsort(res)[-3:][::-1]
            
            best_w1, best_c1 = class_names[top_indices[0]], res[top_indices[0]] * 100
            best_w2, best_c2 = class_names[top_indices[1]], res[top_indices[1]] * 100
            best_w3, best_c3 = class_names[top_indices[2]], res[top_indices[2]] * 100
            
            print("\n" + "="*50)
            print(f"🎯 KẾT QUẢ DỊCH CHÍNH THỨC CHO VIDEO: {video_name}")
            print(f"  👉 Top 1: 『 {best_w1} 』 ({best_c1:.1f}%)")
            print(f"  👉 Top 2: {best_w2} ({best_c2:.1f}%)")
            print(f"  👉 Top 3: {best_w3} ({best_c3:.1f}%)")
            print("="*50 + "\n")

            # Cập nhật màn hình kết quả dừng lại (Sử dụng raw_annotated_image để KHÔNG bị chồng chữ)
            if raw_annotated_image is not None:
                final_img = raw_annotated_image.copy()
                final_img = draw_vietnamese_text(final_img, f"Video: {video_name}", (20, 15), font_size=26, color=(255, 255, 255))
                final_img = draw_vietnamese_text(final_img, f"1. 『 {best_w1} 』 ({best_c1:.1f}%)", (20, 55), font_size=34, color=(0, 255, 0))
                final_img = draw_vietnamese_text(final_img, f"2. {best_w2} ({best_c2:.1f}%)   |   3. {best_w3} ({best_c3:.1f}%)", (20, 105), font_size=28, color=(0, 255, 255))
                final_img = draw_vietnamese_text(final_img, "📌 DỪNG XÁC ĐỊNH: Bấm [SPACE] hoặc [n] để sang video tiếp theo", (20, 155), font_size=24, color=(255, 255, 0))

                cv2.imshow(WINDOW_NAME, final_img)

                # Đợi người dùng bấm nút SPACE hoặc n hoặc q, hoặc đóng nút X
                print(f"⏸️ Đã xác định xong! Màn hình đang TẠM DỪNG. Bấm [SPACE] hoặc [n] để xem video tiếp theo.")
                while True:
                    k = cv2.waitKey(100) & 0xFF
                    if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                        print("🛑 Cửa sổ đã bị đóng bởi người dùng.")
                        return False
                    if k == ord('q'):
                        return False
                    elif k == ord(' ') or k == ord('n'):
                        break

        return True
    finally:
        cap.release()

def main():
    print("="*60)
    print(" PROGRAM TEST DỊCH VIDEO KÝ HIỆU TIẾNG VIỆT (OFFLINE AI)")
    print("="*60)
    
    print("1. Đang nạp từ điển classes.json...")
    try:
        with open(CLASSES_PATH, 'r', encoding='utf-8') as f:
            class_names = json.load(f)
        print(f"  ✅ Từ điển: {len(class_names)} từ vựng.")
    except Exception as e:
        print(f"❌ Lỗi nạp từ điển: {e}")
        return

    print("2. Đang nạp mô hình AI...")
    models_dir = os.path.join(_BASE_DIR, 'models')
    
    from model_loader import load_inference_model
    try:
        model, loaded_path = load_inference_model(models_dir, (MAX_FRAMES, NUM_POINTS, NUM_DIMS), len(class_names))
        print(f"  ✅ Nạp thành công checkpoint: {os.path.basename(loaded_path)}")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return

    # Quét danh sách video trong test_videos/input_videos
    valid_exts = ('*.mp4', '*.avi', '*.mov', '*.mkv')
    video_files = []
    for ext in valid_exts:
        video_files.extend(glob.glob(os.path.join(TEST_VIDEOS_DIR, ext)))

    # Nếu thư mục trống, thử tìm video mẫu trong Dataset
    if not video_files:
        print(f"\n⚠️ Thư mục '{TEST_VIDEOS_DIR}' đang trống!")
        print("  👉 Vui lòng thả các video clip .mp4 / .avi vào thư mục này để thử nghiệm.")
        
        sample_dataset_dir = os.path.join(_BASE_DIR, 'Dataset', 'raw', 'raw')
        sample_videos = glob.glob(os.path.join(sample_dataset_dir, '**', '*.mp4'), recursive=True)
        if sample_videos:
            print(f"  💡 Tìm thấy {len(sample_videos)} video mẫu trong Dataset. Sẽ chạy thử nghiệm video mẫu...")
            video_files = sample_videos[:5]
        else:
            return

    print(f"\n🎯 Tìm thấy {len(video_files)} video để test:")
    for f in video_files:
        print(f" - {os.path.basename(f)}")

    print("\n--------------------------------------------------")
    print(" HƯỚNG DẪN ĐIỀU KHIỂN KHI PHÁT VIDEO:")
    print(" - Khi kết thúc 1 video: Màn hình tự động DỪNG và in KẾT QUẢ DỊCH.")
    print(" - Phím [SPACE] / [n]:     Chuyển sang video tiếp theo")
    print(" - Phím [q]:               Thoát chương trình")
    print("--------------------------------------------------\n")

    for v_path in video_files:
        cont = process_single_video(v_path, model, class_names)
        if not cont:
            break

    cv2.destroyAllWindows()
    print("🎉 Hoàn tất toàn bộ chương trình test video!")

if __name__ == '__main__':
    main()
