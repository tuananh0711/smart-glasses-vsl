import os
import sys
import json
import time
import argparse
import numpy as np
from collections import deque

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# -----------------------------------------------------------------------------
# NẠP TRÌNH SUY LUẬN TFLITE (TỰ ĐỘNG THÍCH ỨNG RASPBERRY PI OS / PC)
# ADR-001: Offline Edge AI Pipeline
# -----------------------------------------------------------------------------
try:
    import tflite_runtime.interpreter as tflite
    print("✅ Đã nạp tflite_runtime.interpreter (Tối ưu cho Raspberry Pi)")
except ImportError:
    import tensorflow.lite as tflite
    print("ℹ️ Dùng tensorflow.lite.Interpreter (Môi trường PC/Development)")

import cv2
import mediapipe as mp

# -----------------------------------------------------------------------------
# NẠP ENGINE TTS PHÁT ÂM THÀNH OFFLINE QUA LOA KÍNH (ADR-004)
# -----------------------------------------------------------------------------
try:
    import pyttsx3
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 160) # Tốc độ nói
    HAS_TTS = True
    print("✅ Đã khởi tạo engine TTS Offline (Phát loa kính thông minh)")
except Exception as e:
    HAS_TTS = False
    print(f"⚠️ Không thể nạp pyttsx3: {e}. (Sẽ chạy chế độ im lặng/No-Audio)")

def speak_offline_text(text):
    """Phát âm thanh tiếng Việt ra loa kính theo ADR-004."""
    if HAS_TTS and text:
        try:
            tts_engine.say(text)
            tts_engine.runAndWait()
        except Exception as e:
            print(f"⚠️ Lỗi phát loa TTS: {e}")

# -----------------------------------------------------------------------------
# HÀM CẤU HÌNH & HÀM BỔ TRỢ
# -----------------------------------------------------------------------------
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_TFLITE_PATH = os.path.join(_BASE_DIR, 'models', 'vsl_bigru_attention.tflite')
CLASSES_PATH = os.path.join(_BASE_DIR, 'models', 'classes.json')

MAX_FRAMES = 60
NUM_POINTS = 48
NUM_DIMS = 3

mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)

def extract_keypoints_48(results):
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

def compute_hand_motion(prev_kp, curr_kp):
    if prev_kp is None or curr_kp is None:
        return 0.0
    prev_pts, curr_pts = [], []
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

def temporal_resample_and_pad(gesture_list, max_frames=60):
    T = len(gesture_list)
    if T == 0:
        return np.zeros((max_frames, 48, 3))
    if T >= max_frames:
        indices = np.linspace(0, T - 1, max_frames, dtype=int)
        return np.array([gesture_list[idx] for idx in indices])
    else:
        resampled = list(gesture_list)
        zero_frame = np.zeros((48, 3))
        while len(resampled) < max_frames:
            resampled.append(zero_frame)
        return np.array(resampled)

# -----------------------------------------------------------------------------
# LUỒNG CHÍNH EDGE AI RASPBERRY PI
# -----------------------------------------------------------------------------
def run_pi_edge_ai(model_path, enable_gui=False, enable_tts=True):
    print("==================================================")
    print("👓 RASPBERRY PI EDGE AI CENTER (OFFLINE PIPELINE)")
    print("==================================================")
    print(f"  • Model Path:  {os.path.basename(model_path)}")
    print(f"  • Audio TTS:   {'BẬT (Loa kính)' if enable_tts else 'TẮT'}")
    print(f"  • GUI Display: {'BẬT (Debug Window)' if enable_gui else 'TẮT (Headless - ADR-004)'}")

    with open(CLASSES_PATH, 'r', encoding='utf-8') as f:
        class_names = json.load(f)

    # Nạp TFLite Interpreter
    interpreter = tflite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Mở Camera
    if os.name == 'nt':
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Không thể kết nối với phần cứng Camera!")
        return

    # Cấu hình 4-State Machine
    PRE_ROLL_FRAMES = 5
    START_CONFIRM_FRAMES = 3
    END_STILL_FRAMES = 12
    HANDS_MISSING_FRAMES = 8
    MIN_GESTURE_FRAMES = 10
    MAX_GESTURE_FRAMES = 150

    START_MOTION_THRESHOLD = 0.025
    END_MOTION_THRESHOLD = 0.010
    CONFIDENCE_THRESHOLD = 0.55
    TOP1_TOP2_MARGIN = 0.12

    state = "IDLE"
    pre_roll_buffer = deque(maxlen=PRE_ROLL_FRAMES)
    gesture_buffer = []
    
    arming_counter = 0
    still_counter = 0
    missing_hands_counter = 0
    cooldown_counter = 0
    smoothed_motion = 0.0
    prev_keypoints = None
    sentence_list = deque(maxlen=5)

    def reset_state():
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

    print("\n🟢 PIPELINE ĐÃ SẴN SÀNG! Đang lắng nghe ký hiệu từ Camera...")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        raw_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        raw_rgb.flags.writeable = False
        results = holistic.process(raw_rgb)

        keypoints = extract_keypoints_48(results)
        is_hands_present = (results.left_hand_landmarks is not None) or (results.right_hand_landmarks is not None)

        raw_motion = compute_hand_motion(prev_keypoints, keypoints)
        smoothed_motion = 0.7 * smoothed_motion + 0.3 * raw_motion
        prev_keypoints = keypoints

        # ----------------------------------------------------
        # STATE MACHINE LOGIC
        # ----------------------------------------------------
        if cooldown_counter > 0:
            cooldown_counter -= 1
            state = "IDLE"
            pre_roll_buffer.clear()
            arming_counter = 0
            smoothed_motion = 0.0
            prev_keypoints = None

        elif state == "IDLE":
            pre_roll_buffer.append(keypoints)
            pre_roll_ready = (len(pre_roll_buffer) == PRE_ROLL_FRAMES)
            if pre_roll_ready and is_hands_present and smoothed_motion > START_MOTION_THRESHOLD:
                state = "ARMING"
                arming_counter = 1

        elif state == "ARMING":
            pre_roll_buffer.append(keypoints)
            if is_hands_present and smoothed_motion > START_MOTION_THRESHOLD:
                arming_counter += 1
                if arming_counter >= START_CONFIRM_FRAMES:
                    state = "RECORDING"
                    gesture_buffer = list(pre_roll_buffer)
                    arming_counter = 0
                    still_counter = 0
                    missing_hands_counter = 0
                    print("🎬 [Pi-EdgeAI]: Bắt đầu thu động tác ký hiệu...")
            else:
                state = "IDLE"
                arming_counter = 0

        elif state == "RECORDING":
            gesture_buffer.append(keypoints)

            if not is_hands_present:
                missing_hands_counter += 1
            else:
                missing_hands_counter = 0

            if smoothed_motion < END_MOTION_THRESHOLD:
                still_counter += 1
            else:
                still_counter = 0

            should_finalize = False
            if missing_hands_counter >= HANDS_MISSING_FRAMES:
                should_finalize = True
                if len(gesture_buffer) > missing_hands_counter:
                    gesture_buffer = gesture_buffer[:-missing_hands_counter]
            elif still_counter >= END_STILL_FRAMES and len(gesture_buffer) >= MIN_GESTURE_FRAMES:
                should_finalize = True
                trim_count = max(0, still_counter - 3)
                if trim_count > 0 and len(gesture_buffer) > trim_count:
                    gesture_buffer = gesture_buffer[:-trim_count]
            elif len(gesture_buffer) >= MAX_GESTURE_FRAMES:
                should_finalize = True

            if should_finalize:
                if len(gesture_buffer) < MIN_GESTURE_FRAMES:
                    reset_state()
                else:
                    state = "FINALIZING"

        if state == "FINALIZING":
            T = len(gesture_buffer)
            sequence_60 = temporal_resample_and_pad(gesture_buffer, MAX_FRAMES)
            input_data = np.expand_dims(sequence_60, axis=0).astype(np.float32)
            input_data = np.reshape(input_data, (1, MAX_FRAMES, NUM_POINTS * NUM_DIMS))

            # TFLite Inference
            t0 = time.perf_counter()
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()
            res = interpreter.get_tensor(output_details[0]['index'])[0]
            t_infer = (time.perf_counter() - t0) * 1000

            top_idxs = np.argsort(res)[-2:][::-1]
            best_idx, second_idx = top_idxs[0], top_idxs[1]
            c1, c2 = res[best_idx], res[second_idx]
            margin = c1 - c2
            word = class_names[best_idx]

            if c1 >= CONFIDENCE_THRESHOLD and margin >= TOP1_TOP2_MARGIN:
                sentence_list.append(word)
                full_sentence = " ".join(sentence_list)
                print(f"🔊 [DỊCH THÀNH CÔNG]: 『 {word} 』 ({c1*100:.1f}%) | Latency: {t_infer:.1f} ms | Câu: {full_sentence}")
                
                # PHÁT ÂM THÀNH QUA LOA KÍNH THÔNG MINH (ADR-004)
                if enable_tts:
                    speak_offline_text(word)
            else:
                print(f"⚠️ [CHƯA CHẮC CHẮN]: {word} ({c1*100:.1f}%) | Margin: {margin*100:.1f}%")

            reset_state()

        if enable_gui:
            cv2.imshow("Raspberry Pi Edge AI Debug", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    if enable_gui:
        cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Raspberry Pi Edge AI Sign Language Translator")
    parser.add_argument('--model', type=str, default=DEFAULT_TFLITE_PATH, help="Path to TFLite model")
    parser.add_argument('--show', action='store_true', help="Enable OpenCV Debug Window")
    parser.add_argument('--no_tts', action='store_true', help="Disable Speaker TTS Audio Output")
    args = parser.parse_args()

    run_pi_edge_ai(args.model, enable_gui=args.show, enable_tts=not args.no_tts)
