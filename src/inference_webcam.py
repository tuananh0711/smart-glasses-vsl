import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import json
import sys
import glob
import argparse
from collections import deque
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from model import build_gru_model, build_bigru_attention_model

from PIL import ImageFont, ImageDraw, Image

WINDOW_NAME = "TEST AI KINH THONG MINH"


def get_screen_size():
    """Return the primary display size; keep a safe fallback off Windows."""
    if os.name == 'nt':
        import ctypes
        user32 = ctypes.windll.user32
        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    return 1280, 720


def resize_to_fill(image, target_width, target_height):
    """Scale and center-crop an image to fill the target without distortion."""
    height, width = image.shape[:2]
    scale = max(target_width / width, target_height / height)
    resized_width = max(target_width, int(round(width * scale)))
    resized_height = max(target_height, int(round(height * scale)))
    interpolation = cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
    resized = cv2.resize(image, (resized_width, resized_height), interpolation=interpolation)
    left = (resized_width - target_width) // 2
    top = (resized_height - target_height) // 2
    return resized[top:top + target_height, left:left + target_width]


def maximize_window(window_name, fallback_width, fallback_height):
    """Maximize an OpenCV window while retaining the native title bar."""
    if os.name != 'nt':
        cv2.resizeWindow(window_name, fallback_width, fallback_height)
        return fallback_width, fallback_height

    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    hwnd = user32.FindWindowW(None, window_name)
    if not hwnd:
        cv2.resizeWindow(window_name, fallback_width, fallback_height)
        return fallback_width, fallback_height

    user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE
    user32.UpdateWindow(hwnd)
    user32.SetForegroundWindow(hwnd)
    # Let Windows finish the maximize/layout transition before measuring the
    # client area. Reading it immediately can transiently return 1x1 pixels.
    for _ in range(8):
        cv2.waitKey(15)
    rect = wintypes.RECT()
    if user32.GetClientRect(hwnd, ctypes.byref(rect)):
        client_width = rect.right - rect.left
        client_height = rect.bottom - rect.top
        if client_width >= 640 and client_height >= 480:
            return client_width, client_height
    # A maximized desktop window keeps the title bar and taskbar, so reserve
    # a small vertical margin instead of ever resizing a frame to a tiny area.
    return fallback_width, max(480, fallback_height - 90)


def draw_status_panel(image, word_text, sentence_text, status_text, conf_threshold):
    """Vẽ bảng trạng thái dịch: Từ hiện tại (giữ nguyên), Câu ghép (nối tiếp), và Tiến trình AI."""
    overlay = image.copy()
    panel_height = min(180, image.shape[0])
    cv2.rectangle(overlay, (0, 0), (image.shape[1], panel_height), (18, 18, 18), -1)
    image = cv2.addWeighted(overlay, 0.72, image, 0.28, 0)
    
    # Dòng 1: Từ vừa nhận diện (Vàng chanh) - Giữ nguyên không bị mất
    image = draw_vietnamese_text(image, f"Từ: {word_text}", (24, 12), 32, (0, 255, 255))
    # Dòng 2: Câu ghép nối tiếp (Xanh lá) - Tự động nối tiếp các từ
    image = draw_vietnamese_text(image, f"Câu: {sentence_text}", (24, 56), 32, (0, 255, 0))
    # Dòng 3: Trạng thái hệ thống + Ngưỡng tin cậy (Vàng cam)
    image = draw_vietnamese_text(
        image, f"Trạng thái: {status_text} | Ngưỡng: {conf_threshold*100:.0f}%", (24, 102), 24, (255, 220, 80)
    )
    # Dòng 4: Hướng dẫn phím nóng (Xám sáng)
    return draw_vietnamese_text(
        image, "Phím: [C] Xóa câu  |  [ [ / ] ] Đổi ngưỡng tin cậy  |  [Q] Thoát", (24, 138), 20, (200, 200, 200)
    )

def draw_vietnamese_text(img, text, position, font_size=36, color=(0, 255, 0)):
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
            
    # Vẽ chữ tiếng Việt đầy đủ dấu (Vẽ bóng chữ đen phía sau để nhìn rõ trên mọi nền)
    x, y = position
    draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=(color[2], color[1], color[0]))
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# Cấu hình đường dẫn
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(_BASE_DIR, 'models', 'vsl_gru_baseline.keras')
CLASSES_PATH = os.path.join(_BASE_DIR, 'models', 'classes.json')
MAX_FRAMES = 60 # Cửa sổ trượt
NUM_POINTS = 48 # 42 điểm bàn tay + 6 điểm khớp chính
NUM_DIMS = 3

# Khởi tạo MediaPipe
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

def extract_keypoints_48(results):
    """
    Trích xuất 48 điểm và chuẩn hóa giống hệt preprocess.py
    (Translation + Scale Normalization)
    """
    pose = np.zeros((6, 3))
    center_x, center_y, center_z = 0.5, 0.5, 0.0
    scale = 1.0
    
    if results.pose_landmarks:
        for i, idx in enumerate([11, 12, 13, 14, 15, 16]):
            res = results.pose_landmarks.landmark[idx]
            if hasattr(res, 'visibility') and res.visibility > 0.5:
                pose[i] = [res.x, res.y, res.z]
            elif not hasattr(res, 'visibility'):
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

    keypoints = np.concatenate([pose, lh, rh])
    
    for i in range(len(keypoints)):
        if not np.array_equal(keypoints[i], [0.0, 0.0, 0.0]):
            keypoints[i][0] = (keypoints[i][0] - center_x) / scale
            keypoints[i][1] = (keypoints[i][1] - center_y) / scale
            keypoints[i][2] = (keypoints[i][2] - center_z) / scale

    return keypoints

def temporal_resample_and_pad(gesture_list, max_frames=60):
    """
    Chuẩn hóa chuỗi T frame về đúng MAX_FRAMES (60) khớp 100% với preprocess.py:
    - Nếu T >= 60: np.linspace(0, T - 1, 60) để co nén về 60 frame.
    - Nếu T < 60: Giữ T frame độc nhất và Zero-padding ở cuối cho đủ 60 frame.
    """
    T = len(gesture_list)
    if T == 0:
        return np.zeros((max_frames, 48, 3))
    
    if T >= max_frames:
        indices = np.linspace(0, T - 1, max_frames, dtype=int)
        resampled = [gesture_list[idx] for idx in indices]
        return np.array(resampled)
    else:
        resampled = list(gesture_list)
        zero_frame = np.zeros((48, 3))
        while len(resampled) < max_frames:
            resampled.append(zero_frame)
        return np.array(resampled)


def compute_hand_motion(prev_kp, curr_kp):
    """Tính vận tốc chuyển động trung vị (Median Motion) của bàn tay và cổ tay giữa 2 frame."""
    if prev_kp is None or curr_kp is None:
        return 0.0
    prev_pts = []
    curr_pts = []
    # Lấy các điểm cổ tay (4, 5) và 42 điểm bàn tay (6..47)
    for idx in range(4, 48):
        p_prev = prev_kp[idx]
        p_curr = curr_kp[idx]
        if not np.array_equal(p_prev, [0.0, 0.0, 0.0]) and not np.array_equal(p_curr, [0.0, 0.0, 0.0]):
            prev_pts.append(p_prev)
            curr_pts.append(p_curr)
            
    if len(prev_pts) == 0:
        return 0.0
        
    diffs = np.linalg.norm(np.array(curr_pts) - np.array(prev_pts), axis=1)
    return float(np.median(diffs))


def parse_args():
    parser = argparse.ArgumentParser(description="Webcam Live Sign Language Inference & Sentence Builder")
    parser.add_argument('--conf', type=float, default=0.10, help="Ngưỡng độ tin cậy tối thiểu để nhận diện từ (Mặc định: 0.10 / 10%%)")
    parser.add_argument('--margin', type=float, default=0.02, help="Khoảng cách tối thiểu giữa Top 1 và Top 2 (Mặc định: 0.02 / 2%%)")
    parser.add_argument('--camera', type=int, default=0, help="ID Camera (Mặc định: 0)")
    parser.add_argument('--max_sentence', type=int, default=20, help="Số từ tối đa trong câu hiển thị (Mặc định: 20)")
    return parser.parse_args()


def main():
    args = parse_args()
    conf_threshold = args.conf
    margin_threshold = args.margin

    print("Đang tải từ điển...")
    try:
        with open(CLASSES_PATH, 'r', encoding='utf-8') as f:
            class_names = json.load(f)
    except Exception as e:
        print(f"Lỗi đọc file classes.json: {e}")
        return

    print("Đang tải bộ não AI (GRU/LSTM 48 điểm)...")
    models_dir = os.path.join(_BASE_DIR, 'models')
    from model_loader import load_inference_model
    try:
        model, loaded_path = load_inference_model(models_dir, (MAX_FRAMES, NUM_POINTS, NUM_DIMS), len(class_names))
        print(f"  ✅ Nạp thành công checkpoint: {os.path.basename(loaded_path)}")
    except Exception as e:
        print(f"❌ Lỗi tải mô hình: {e}")
        return
        
    print(f"Mở Camera {args.camera}... (Sẵn sàng Picamera2 cho Raspberry Pi)")
    if os.name == 'nt':
        cap = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(args.camera)

    if not cap.isOpened():
        print("Không thể mở camera. Hãy đóng ứng dụng khác đang sử dụng webcam.")
        return

    # HighGUI on Windows may not create a native HWND until the first imshow.
    # Bootstrap it before maximizing/focusing so IDE-launched processes are visible.
    first_ok, first_frame = cap.read()
    if not first_ok or first_frame is None:
        print("Camera đã mở nhưng không trả về khung hình đầu tiên.")
        cap.release()
        return

    screen_width, screen_height = get_screen_size()
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL | cv2.WINDOW_FREERATIO)
    cv2.imshow(WINDOW_NAME, first_frame)
    cv2.waitKey(1)
    window_width, window_height = maximize_window(WINDOW_NAME, screen_width, screen_height)
    if hasattr(cv2, 'WND_PROP_TOPMOST'):
        cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)

    # =========================================================================
    # CẤU HÌNH KIẾN TRÚC 4 TRẠNG THÁI CHUẨN (EXPLICIT 4-STATE MACHINE)
    # =========================================================================
    PRE_ROLL_FRAMES = 5         # Đệm 5 frame tiền động tác
    START_CONFIRM_FRAMES = 3    # Duy trì chuyển động 3 frame trong ARMING
    END_STILL_FRAMES = 12       # Đứng yên 12 frame -> Chốt từ
    HANDS_MISSING_FRAMES = 8    # Tay biến mất 8 frame -> Chốt từ
    MIN_GESTURE_FRAMES = 10     # Độ dài tối thiểu của ký hiệu hợp lệ
    MAX_GESTURE_FRAMES = 150    # Giới hạn tối đa buffer

    START_MOTION_THRESHOLD = 0.025 # Ngưỡng vận tốc bắt đầu ký hiệu
    END_MOTION_THRESHOLD = 0.010   # Ngưỡng vận tốc kết thúc ký hiệu

    # Các biến quản lý State Machine & Hiển thị từ/câu
    state = "IDLE"
    pre_roll_buffer = deque(maxlen=PRE_ROLL_FRAMES)
    gesture_buffer = []
    
    arming_counter = 0
    still_counter = 0
    missing_hands_counter = 0
    cooldown_counter = 0
    
    smoothed_motion = 0.0
    prev_keypoints = None
    
    sentence_list = deque(maxlen=args.max_sentence)
    last_word_display = "(Chờ ký hiệu...)"
    pipeline_status_text = "CHỜ KÝ HIỆU (IDLE)"

    def reset_segmentation_state():
        """Reset sạch toàn bộ bộ nhớ phân đoạn để tránh ô nhiễm chuỗi giữa 2 từ."""
        nonlocal state, gesture_buffer, arming_counter, still_counter
        nonlocal missing_hands_counter, cooldown_counter, smoothed_motion, prev_keypoints
        gesture_buffer.clear()
        pre_roll_buffer.clear()
        arming_counter = 0
        still_counter = 0
        missing_hands_counter = 0
        smoothed_motion = 0.0
        prev_keypoints = None
        cooldown_counter = 10
        state = "IDLE"

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1)
        raw_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        raw_rgb.flags.writeable = False
        results = holistic.process(raw_rgb)
        
        image = frame.copy()

        # 1. Vẽ Landmark 2 tay
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
            h_f, w_f, _ = image.shape
            pts = {}
            for idx in [11, 12, 13, 14, 15, 16]:
                lm = results.pose_landmarks.landmark[idx]
                vis = getattr(lm, 'visibility', 1.0)
                if vis > 0.5:
                    cx, cy = int(lm.x * w_f), int(lm.y * h_f)
                    pts[idx] = (cx, cy)
                    cv2.circle(image, (cx, cy), 6, (0, 255, 255), -1)
                    cv2.circle(image, (cx, cy), 8, (0, 0, 255), 2)

            for p1, p2 in [(11, 12), (11, 13), (13, 15), (12, 14), (14, 16)]:
                if p1 in pts and p2 in pts:
                    cv2.line(image, pts[p1], pts[p2], (0, 255, 255), 3)

        # 3. Trích xuất đặc trưng & Tính vận tốc chuyển động
        keypoints = extract_keypoints_48(results)
        is_hands_present = (results.left_hand_landmarks is not None) or (results.right_hand_landmarks is not None)
        
        raw_motion = compute_hand_motion(prev_keypoints, keypoints)
        smoothed_motion = 0.7 * smoothed_motion + 0.3 * raw_motion
        prev_keypoints = keypoints

        # =========================================================================
        # ĐIỀU KHIỂN CHÍNH XÁC KIẾN TRÚC 4 TRẠNG THÁI (STATE MACHINE)
        # =========================================================================
        if cooldown_counter > 0:
            cooldown_counter -= 1
            state = "IDLE"
            pre_roll_buffer.clear()
            arming_counter = 0
            smoothed_motion = 0.0
            prev_keypoints = None
            pipeline_status_text = "COOLDOWN (Sẵn sàng đón từ tiếp theo)"
        
        elif state == "IDLE":
            pre_roll_buffer.append(keypoints)
            pre_roll_ready = (len(pre_roll_buffer) == PRE_ROLL_FRAMES)
            if pre_roll_ready and is_hands_present and smoothed_motion > START_MOTION_THRESHOLD:
                state = "ARMING"
                arming_counter = 1
                pipeline_status_text = "ARMING (Phát hiện chuyển động...)"
                print("🟡 [STATE]: IDLE -> ARMING (Phát hiện chuyển động)")
            else:
                arming_counter = 0
                if not pre_roll_ready:
                    pipeline_status_text = f"IDLE (Chuẩn bị bộ đệm {len(pre_roll_buffer)}/{PRE_ROLL_FRAMES})"
                else:
                    pipeline_status_text = "CHỜ KÝ HIỆU (Đưa tay lên để bắt đầu)"

        elif state == "ARMING":
            pre_roll_buffer.append(keypoints)
            if is_hands_present and smoothed_motion > START_MOTION_THRESHOLD:
                arming_counter += 1
                pipeline_status_text = f"ARMING (Xác nhận chuyển động {arming_counter}/{START_CONFIRM_FRAMES})"
                if arming_counter >= START_CONFIRM_FRAMES:
                    state = "RECORDING"
                    gesture_buffer = list(pre_roll_buffer)
                    arming_counter = 0
                    still_counter = 0
                    missing_hands_counter = 0
                    pipeline_status_text = "RECORDING (Bắt đầu thu ký hiệu)"
                    print("🎬 [STATE]: ARMING -> RECORDING (Đã xác nhận, bắt đầu thu ký hiệu)")
            else:
                # Chuyển động bị hủy giữa chừng -> Quay về IDLE
                state = "IDLE"
                arming_counter = 0
                pipeline_status_text = "CHỜ KÝ HIỆU (Hủy ARMING do dừng cử chỉ)"
                print("⚪ [STATE]: ARMING -> IDLE (Chuyển động không đủ dài, hủy ARMING)")

        elif state == "RECORDING":
            gesture_buffer.append(keypoints)
            progress_pct = min(100, int(len(gesture_buffer) / MAX_GESTURE_FRAMES * 100))
            pipeline_status_text = f"ĐANG THU KÝ HIỆU... [{len(gesture_buffer)} frames - {progress_pct}%]"

            if not is_hands_present:
                missing_hands_counter += 1
            else:
                missing_hands_counter = 0

            if smoothed_motion < END_MOTION_THRESHOLD:
                still_counter += 1
            else:
                still_counter = 0

            # Kiểm tra điều kiện ngắt/chốt từ
            should_finalize = False
            if missing_hands_counter >= HANDS_MISSING_FRAMES:
                should_finalize = True
                # Loại bỏ các frame rác không thấy tay ở cuối chuỗi
                if len(gesture_buffer) > missing_hands_counter:
                    gesture_buffer = gesture_buffer[:-missing_hands_counter]
            elif still_counter >= END_STILL_FRAMES and len(gesture_buffer) >= MIN_GESTURE_FRAMES:
                should_finalize = True
                # Giữ lại 3 frame tĩnh cuối cùng, loại bỏ 9 frame tĩnh thừa
                trim_count = max(0, still_counter - 3)
                if trim_count > 0 and len(gesture_buffer) > trim_count:
                    gesture_buffer = gesture_buffer[:-trim_count]
            elif len(gesture_buffer) >= MAX_GESTURE_FRAMES:
                should_finalize = True

            if should_finalize:
                if len(gesture_buffer) < MIN_GESTURE_FRAMES:
                    print("⚠️ [STATE]: Chuỗi quá ngắn, bỏ qua (Hủy mẫu).")
                    reset_segmentation_state()
                else:
                    state = "FINALIZING"
                    print(f"🎯 [STATE]: RECORDING -> FINALIZING (Chốt thu {len(gesture_buffer)} frames sau khi Trim)")

        if state == "FINALIZING":
            pipeline_status_text = "FINALIZING (Đang phân tích AI...)"
            
            # Resampling và Zero-padding khớp 100% với preprocess.py
            sequence_60 = temporal_resample_and_pad(gesture_buffer, MAX_FRAMES)
            T = len(gesture_buffer)

            input_data = np.expand_dims(sequence_60, axis=0)
            input_data = np.reshape(input_data, (1, MAX_FRAMES, NUM_POINTS * NUM_DIMS))

            res = model.predict(input_data, verbose=0)[0]
            top_idxs = np.argsort(res)[-2:][::-1]

            best_idx, second_idx = top_idxs[0], top_idxs[1]
            c1, c2 = res[best_idx], res[second_idx]
            margin = c1 - c2
            word = class_names[best_idx]

            # Kiểm tra điều kiện nghiệm thu
            if c1 >= conf_threshold and margin >= margin_threshold:
                sentence_list.append(word)
                last_word_display = f"{word} ({c1*100:.1f}%)"
                pipeline_status_text = f"✅ ĐÃ NHẬN DIỆN: [{word}] ({c1*100:.1f}%)"
                print(f"✅ [DỰ ĐOÁN THÀNH CÔNG]: {word} | Conf: {c1*100:.1f}% | Margin: {margin*100:.1f}% | Frames: {T} | Câu: {' '.join(sentence_list)}")
            else:
                last_word_display = f"{word} ({c1*100:.1f}% - Thấp)"
                pipeline_status_text = f"⚠️ CHƯA ĐỦ TIN CẬY: {word} ({c1*100:.1f}% < {conf_threshold*100:.0f}%)"
                print(f"⚠️ [CHƯA CHẮC CHẮN]: {word} | Conf: {c1*100:.1f}% | Margin: {margin*100:.1f}% (Cần >= {conf_threshold*100:.0f}%)")

            # Reset sạch bộ nhớ phân đoạn để đón từ tiếp theo
            reset_segmentation_state()

        # Hiển thị giao diện
        image = resize_to_fill(image, window_width, window_height)
        display_sentence = " ".join(sentence_list) or "(Chưa có từ)"
        image = draw_status_panel(image, last_word_display, display_sentence, pipeline_status_text, conf_threshold)

        cv2.imshow(WINDOW_NAME, image)
        if hasattr(cv2, 'WND_PROP_TOPMOST'):
            cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)

        key = cv2.waitKey(10) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c') or key == ord('C'):
            sentence_list.clear()
            last_word_display = "(Đã xóa câu)"
            pipeline_status_text = "ĐÃ XÓA CÂU (Bắt đầu câu mới)"
            print("🧹 [RESET]: Đã xóa toàn bộ câu hiện tại.")
        elif key == ord('['):
            conf_threshold = max(0.02, round(conf_threshold - 0.02, 2))
            pipeline_status_text = f"ĐÃ GIẢM NGƯỠNG: {conf_threshold*100:.0f}%"
            print(f"⚙️ [CONFIG]: Ngưỡng tin cậy giảm xuống: {conf_threshold*100:.1f}%")
        elif key == ord(']'):
            conf_threshold = min(0.95, round(conf_threshold + 0.02, 2))
            pipeline_status_text = f"ĐÃ TĂNG NGƯỠNG: {conf_threshold*100:.0f}%"
            print(f"⚙️ [CONFIG]: Ngưỡng tin cậy tăng lên: {conf_threshold*100:.1f}%")
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
