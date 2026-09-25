import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
import cv2
import mediapipe as mp
import numpy as np
import json
import sys
import argparse
import datetime
from collections import deque
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from segmentation import (
    Segmenter, CURRENT_CONFIG, P1_CONFIG, is_active_hand,
    extract_keypoints_48, MAX_FRAMES, NUM_POINTS, NUM_DIMS,
)

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


def setup_gui_window(window_name, default_width=1280, default_height=720):
    """Tạo cửa sổ OpenCV vừa màn hình, căn giữa, foreground (không phá viewport HighGUI)."""
    screen_width, screen_height = get_screen_size()
    target_width = min(default_width, max(640, screen_width - 80))
    target_height = min(default_height, max(480, screen_height - 120))

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, target_width, target_height)

    if os.name == 'nt':
        import ctypes
        user32 = ctypes.windll.user32
        hwnd = user32.FindWindowW(None, window_name)
        if hwnd:
            pos_x = max(0, (screen_width - target_width) // 2)
            pos_y = max(0, (screen_height - target_height) // 2)
            user32.SetWindowPos(hwnd, -1, pos_x, pos_y, target_width, target_height, 0x0040)
            user32.ShowWindow(hwnd, 5)
            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)

    return target_width, target_height


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

    x, y = position
    draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=(color[2], color[1], color[0]))
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


def draw_status_panel(image, word_text, sentence_text, status_text, conf_threshold, hand_info="", flip_mode=False):
    """Vẽ bảng trạng thái dịch: Từ hiện tại, Câu ghép, Tiến trình AI, và Bàn tay hoạt động."""
    overlay = image.copy()
    panel_height = min(180, image.shape[0])
    cv2.rectangle(overlay, (0, 0), (image.shape[1], panel_height), (18, 18, 18), -1)
    image = cv2.addWeighted(overlay, 0.72, image, 0.28, 0)

    image = draw_vietnamese_text(image, f"Từ: {word_text}", (24, 12), 32, (0, 255, 255))
    image = draw_vietnamese_text(image, f"Câu: {sentence_text}", (24, 56), 32, (0, 255, 0))
    info_line = f"Trạng thái: {status_text} | Ngưỡng: {conf_threshold * 100:.0f}%"
    if hand_info:
        info_line += f" | {hand_info}"
    image = draw_vietnamese_text(image, info_line, (24, 102), 24, (255, 220, 80))
    flip_status = "BẬT (Gương)" if flip_mode else "TẮT (Chuẩn Train)"
    return draw_vietnamese_text(
        image, f"Phím: [C] Xóa câu | [ [ / ] ] Đổi ngưỡng | [F] Lật camera ({flip_status}) | [Q] Thoát",
        (24, 138), 20, (200, 200, 200)
    )


# Cấu hình đường dẫn
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLASSES_PATH = os.path.join(_BASE_DIR, 'models', 'classes.json')

# Khởi tạo MediaPipe
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

from PIL import ImageFont, ImageDraw, Image


def parse_args():
    parser = argparse.ArgumentParser(description="Webcam Live Sign Language Inference & Sentence Builder")
    parser.add_argument('--conf', type=float, default=0.40,
                        help="Ngưỡng tin cậy tối thiểu (mặc định 0.40)")
    parser.add_argument('--margin', type=float, default=0.05,
                        help="Khoảng cách tối thiểu giữa Top 1 và Top 2 (Mặc định: 0.05 / 5%%)")
    parser.add_argument('--camera', type=int, default=0, help="ID Camera (Mặc định: 0)")
    parser.add_argument('--max_sentence', type=int, default=20, help="Số từ tối đa trong câu (Mặc định: 20)")
    parser.add_argument('--flip', action='store_true', help="Lật gương camera (Mặc định TẮT để khớp chirality dữ liệu train)")
    parser.add_argument('--legacy-segmenter', action='store_true',
                        help="Dùng cấu hình phân đoạn TASK-013 (không có stillness end-detector) để A/B")
    parser.add_argument('--log-file', type=str, default='webcam_session.log',
                        help="Đường dẫn file ghi log phiên test (Mặc định: webcam_session.log)")
    return parser.parse_args()


def main():
    args = parse_args()
    conf_threshold = args.conf
    margin_threshold = args.margin
    flip_mode = args.flip

    print("Đang tải từ điển...")
    try:
        with open(CLASSES_PATH, 'r', encoding='utf-8') as f:
            class_names = json.load(f)
    except Exception as e:
        print(f"Lỗi đọc file classes.json: {e}")
        return

    print("Đang tải bộ não AI (48 điểm)...")
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

    # HighGUI trên Windows có thể chưa tạo HWND cho tới imshow đầu tiên.
    first_ok, first_frame = cap.read()
    if not first_ok or first_frame is None:
        print("Camera đã mở nhưng không trả về khung hình đầu tiên.")
        cap.release()
        return

    window_width, window_height = setup_gui_window(WINDOW_NAME, 1280, 720)
    cv2.imshow(WINDOW_NAME, first_frame)
    cv2.waitKey(20)
    if os.name == 'nt':
        import ctypes
        user32 = ctypes.windll.user32
        hwnd = user32.FindWindowW(None, WINDOW_NAME)
        if hwnd:
            user32.ShowWindow(hwnd, 5)
            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)

    seg_config = CURRENT_CONFIG if args.legacy_segmenter else P1_CONFIG
    segmenter = Segmenter(seg_config)
    print(f"⚙️  Bộ phân đoạn: {'TASK-013 (legacy)' if args.legacy_segmenter else 'P1 (stillness end-detector)'}")

    # Khởi tạo log file phiên làm việc
    session_log_path = os.path.join(_BASE_DIR, args.log_file) if not os.path.isabs(args.log_file) else args.log_file
    try:
        with open(session_log_path, 'w', encoding='utf-8') as lf:
            lf.write(f"=== PHIÊN TEST WEBCAM ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===\n")
            lf.write(f"Bộ phân đoạn : {'TASK-013 (legacy)' if args.legacy_segmenter else 'P1 (stillness end-detector)'}\n")
            lf.write(f"Cấu hình     : Conf threshold={conf_threshold * 100:.0f}% | Margin={margin_threshold * 100:.1f}% | Flip={flip_mode}\n")
            lf.write("=" * 65 + "\n\n")
        print(f"📝 Đang ghi log chi tiết vào file: {os.path.basename(session_log_path)}")
    except Exception as e:
        print(f"⚠️ Không thể khởi tạo log file: {e}")

    gesture_count = 0
    sentence_list = deque(maxlen=args.max_sentence)
    last_word_display = "(Chờ ký hiệu...)"
    pipeline_status_text = "CHỜ KÝ HIỆU (Đưa tay lên để bắt đầu)"

    def finalize_segment(frames, reason):
        """Resample + suy luận + cập nhật UI/log cho một cử chỉ đã chốt."""
        nonlocal last_word_display, pipeline_status_text, gesture_count
        gesture_count += 1
        input_data = segmenter.model_input(frames)
        res = model.predict(input_data, verbose=0)[0]
        top_idxs = np.argsort(res)[-5:][::-1]
        best_idx, second_idx = int(top_idxs[0]), int(top_idxs[1])
        c1, c2 = float(res[best_idx]), float(res[second_idx])
        margin = c1 - c2
        word = class_names[best_idx]
        raw_T = len(frames)

        top5_summary = " | ".join([f"{class_names[i]}: {res[i] * 100:.1f}%" for i in top_idxs])
        print(f"📊 [TOP 5]: {top5_summary}")

        if c1 >= conf_threshold and margin >= margin_threshold:
            if len(sentence_list) == 0 or sentence_list[-1] != word:
                sentence_list.append(word)
            last_word_display = f"{word} ({c1 * 100:.1f}%)"
            pipeline_status_text = f"✅ [{word}] ({c1 * 100:.1f}% | {raw_T}f | {reason})"
            status_desc = f"✅ CHẤP NHẬN: [{word}] ({c1 * 100:.1f}%)"
            print(f"✅ [DỰ ĐOÁN]: {word} | Conf: {c1 * 100:.1f}% | Margin: {margin * 100:.1f}% | "
                  f"Frames: {raw_T} | End: {reason} | Câu: {' '.join(sentence_list)}")
        else:
            last_word_display = f"⚠️ Bỏ qua ({word}: {c1 * 100:.1f}%)"
            pipeline_status_text = f"⚠️ TÍN HIỆU YẾU: Bỏ qua [{word}] ({c1 * 100:.1f}% < {conf_threshold * 100:.0f}%)"
            status_desc = f"⚠️ TÍN HIỆU YẾU: Bỏ qua [{word}] ({c1 * 100:.1f}% < {conf_threshold * 100:.0f}%)"
            print(f"⚠️ [CHƯA CHẮC CHẮN]: {word} | Conf: {c1 * 100:.1f}% | Margin: {margin * 100:.1f}% "
                  f"(Cần conf >= {conf_threshold * 100:.0f}%)")

        # Ghi nhận chi tiết vào file log để theo dõi phân tích
        try:
            with open(session_log_path, 'a', encoding='utf-8') as lf:
                now_str = datetime.datetime.now().strftime('%H:%M:%S')
                lf.write(f"[LƯỢT #{gesture_count} Lúc {now_str}]\n")
                lf.write(f"  • Độ dài cử chỉ : {raw_T} frames (~{raw_T / 25.0:.2f}s) | Lý do chốt: {reason}\n")
                lf.write(f"  • Top 5 dự đoán : {top5_summary}\n")
                lf.write(f"  • Kết quả       : {status_desc} | Margin: {margin * 100:.1f}%\n")
                lf.write(f"  • Câu hiện tại  : {' '.join(sentence_list) if sentence_list else '(trống)'}\n\n")
        except Exception:
            pass

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if flip_mode:
                frame = cv2.flip(frame, 1)
            raw_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            raw_rgb.flags.writeable = False
            results = holistic.process(raw_rgb)

            image = frame.copy()

            # Vẽ landmark 2 bàn tay.
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

            # Vẽ 6 điểm pose.
            if results.pose_landmarks:
                h_f, w_f, _ = image.shape
                pts = {}
                for idx in [11, 12, 13, 14, 15, 16]:
                    lm = results.pose_landmarks.landmark[idx]
                    if getattr(lm, 'visibility', 1.0) > 0.5:
                        cx, cy = int(lm.x * w_f), int(lm.y * h_f)
                        pts[idx] = (cx, cy)
                        cv2.circle(image, (cx, cy), 6, (0, 255, 255), -1)
                        cv2.circle(image, (cx, cy), 8, (0, 0, 255), 2)
                for p1, p2 in [(11, 12), (11, 13), (13, 15), (12, 14), (14, 16)]:
                    if p1 in pts and p2 in pts:
                        cv2.line(image, pts[p1], pts[p2], (0, 255, 255), 3)

            # Trích xuất đặc trưng + đẩy vào máy trạng thái DÙNG CHUNG với benchmark.
            keypoints = extract_keypoints_48(results)
            hands_present = (
                is_active_hand(results.left_hand_landmarks, results.pose_landmarks)
                or is_active_hand(results.right_hand_landmarks, results.pose_landmarks)
            )
            finalized = segmenter.feed(keypoints, hands_present)

            if finalized:
                frames, reason = finalized
                finalize_segment(frames, reason)
            else:
                st = segmenter.state
                if st == "IDLE":
                    pipeline_status_text = "CHỜ KÝ HIỆU (Đưa tay lên để bắt đầu)"
                elif st == "ARMING":
                    pipeline_status_text = "ARMING (Xác nhận chuyển động...)"
                elif st == "RECORDING":
                    pipeline_status_text = f"ĐANG THU KÝ HIỆU... [{segmenter.record_len} frames]"

            # Hiển thị giao diện.
            active_hand_names = []
            if is_active_hand(results.left_hand_landmarks, results.pose_landmarks):
                active_hand_names.append("Trái")
            if is_active_hand(results.right_hand_landmarks, results.pose_landmarks):
                active_hand_names.append("Phải")
            hand_info = f"Tay: [{'+'.join(active_hand_names)}]" if active_hand_names else "Tay: [Nghỉ]"

            image = resize_to_fill(image, window_width, window_height)
            display_sentence = " ".join(sentence_list) or "(Chưa có từ)"
            image = draw_status_panel(image, last_word_display, display_sentence,
                                      pipeline_status_text, conf_threshold, hand_info, flip_mode)

            cv2.imshow(WINDOW_NAME, image)
            key = cv2.waitKey(10) & 0xFF
            if key == ord('q'):
                break
            elif key in (ord('c'), ord('C')):
                sentence_list.clear()
                last_word_display = "(Đã xóa câu)"
                pipeline_status_text = "ĐÃ XÓA CÂU (Bắt đầu câu mới)"
                print("🧹 [RESET]: Đã xóa toàn bộ câu hiện tại.")
            elif key == ord('['):
                conf_threshold = max(0.02, round(conf_threshold - 0.02, 2))
                print(f"⚙️ [CONFIG]: Ngưỡng tin cậy giảm xuống: {conf_threshold * 100:.1f}%")
            elif key == ord(']'):
                conf_threshold = min(0.95, round(conf_threshold + 0.02, 2))
                print(f"⚙️ [CONFIG]: Ngưỡng tin cậy tăng lên: {conf_threshold * 100:.1f}%")
            elif key in (ord('f'), ord('F')):
                flip_mode = not flip_mode
                print(f"🔄 [CAMERA]: Chế độ lật gương: {flip_mode}")
            if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        try:
            holistic.close()
        except Exception:
            pass
        print("🛑 Đã giải phóng an toàn tài nguyên Camera và MediaPipe.")


if __name__ == '__main__':
    main()
