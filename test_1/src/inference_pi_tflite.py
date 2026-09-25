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

import queue
import threading

# -----------------------------------------------------------------------------
# KHỞI TẠO ENGINE TTS PHÁT ÂM THÀNH BẤT ĐỒNG BỘ (ADR-004)
# PC-PI-02: Dùng Worker Thread tránh treo vòng lặp camera
# -----------------------------------------------------------------------------
_tts_queue = queue.Queue()
_tts_worker_thread = None

def _tts_worker():
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        try:
            voices = engine.getProperty('voices')
            for v in voices:
                if 'vietnam' in v.name.lower() or 'vi' in v.id.lower() or 'vn' in v.id.lower():
                    engine.setProperty('voice', v.id)
                    break
        except Exception:
            pass
    except Exception as e:
        print(f"⚠️ Worker TTS không thể khởi tạo pyttsx3: {e}")
        return

    while True:
        text = _tts_queue.get()
        if text is None:
            break
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"⚠️ Lỗi phát loa TTS: {e}")
        finally:
            _tts_queue.task_done()

def init_tts():
    """Khởi tạo Background Worker Thread cho TTS chỉ khi cần thiết."""
    global _tts_worker_thread
    if _tts_worker_thread is not None and _tts_worker_thread.is_alive():
        return True
    try:
        _tts_worker_thread = threading.Thread(target=_tts_worker, daemon=True)
        _tts_worker_thread.start()
        print("✅ Đã khởi tạo engine TTS Offline bất đồng bộ (Background Worker Thread)")
        return True
    except Exception as e:
        print(f"⚠️ Không thể khởi tạo thread TTS: {e}")
        return False

def speak_offline_text(text, enable_tts=True):
    """Phát âm thanh tiếng Việt ra loa kính bất đồng bộ theo ADR-004."""
    if enable_tts and text:
        init_tts()
        _tts_queue.put(text)

# -----------------------------------------------------------------------------
# HÀM CẤU HÌNH & HÀM BỔ TRỢ
# -----------------------------------------------------------------------------
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DYNAMIC_MODEL = os.path.join(_BASE_DIR, 'models', 'vsl_bigru_attention_dynamic.tflite')
_FP32_MODEL = os.path.join(_BASE_DIR, 'models', 'vsl_bigru_attention.tflite')
DEFAULT_TFLITE_PATH = _DYNAMIC_MODEL if os.path.exists(_DYNAMIC_MODEL) else _FP32_MODEL
CLASSES_PATH = os.path.join(_BASE_DIR, 'models', 'classes.json')

mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# -----------------------------------------------------------------------------
# LOGIC PHÂN ĐOẠN DÙNG CHUNG (segmentation.py) — bản sao production của
# eval_segmentation.py. Không copy-paste state machine ở nhiều nơi nữa.
# -----------------------------------------------------------------------------
from segmentation import (
    Segmenter, CURRENT_CONFIG, P1_CONFIG, is_active_hand,
    extract_keypoints_48, MAX_FRAMES, NUM_POINTS, NUM_DIMS,
)


# -----------------------------------------------------------------------------
# LUỒNG CHÍNH EDGE AI RASPBERRY PI
# -----------------------------------------------------------------------------
def run_pi_edge_ai(model_path, enable_gui=False, enable_tts=True, flip_camera=False, legacy_segmenter=False):
    print("==================================================")
    print("👓 RASPBERRY PI EDGE AI CENTER (OFFLINE PIPELINE)")
    print("==================================================")
    print(f"  • Model Path:  {os.path.basename(model_path)}")
    print(f"  • Audio TTS:   {'BẬT (Loa kính)' if enable_tts else 'TẮT'}")
    print(f"  • GUI Display: {'BẬT (Debug Window)' if enable_gui else 'TẮT (Headless - ADR-004)'}")
    print(f"  • Flip Camera: {'BẬT (Lật gương)' if flip_camera else 'TẮT (Chuẩn Train AI)'}")

    if not os.path.exists(CLASSES_PATH):
        print(f"❌ Không tìm thấy file classes tại: {CLASSES_PATH}")
        return

    with open(CLASSES_PATH, 'r', encoding='utf-8') as f:
        class_names = json.load(f)

    if not os.path.exists(model_path):
        print(f"❌ Không tìm thấy file model TFLite tại: {model_path}")
        return

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

    # Cấu hình suy luận
    CONFIDENCE_THRESHOLD = 0.40
    TOP1_TOP2_MARGIN = 0.05

    # Máy trạng thái 4 pha DÙNG CHUNG với benchmark eval_segmentation.py.
    seg_config = CURRENT_CONFIG if legacy_segmenter else P1_CONFIG
    segmenter = Segmenter(seg_config)
    print(f"⚙️  [Pi-EdgeAI] Bộ phân đoạn: {'TASK-013 (legacy)' if legacy_segmenter else 'P1 (stillness end-detector)'}")
    sentence_list = deque(maxlen=5)

    print("\n🟢 PIPELINE ĐÃ SẴN SÀNG! Đang lắng nghe ký hiệu từ Camera...")

    def finalize_word(frames, reason):
        raw_T = len(frames)
        input_data = segmenter.model_input(frames)

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
            if not sentence_list or sentence_list[-1] != word:
                sentence_list.append(word)
            full_sentence = " ".join(sentence_list)
            print(f"🔊 [DỊCH THÀNH CÔNG]: 『 {word} 』 ({c1*100:.1f}%) | Latency: {t_infer:.1f} ms | "
                  f"Frames: {raw_T} | End: {reason} | Câu: {full_sentence}")

            # PHÁT ÂM THÀNH QUA LOA KÍNH THÔNG MINH (ADR-004) - BẤT ĐỒNG BỘ
            if enable_tts:
                speak_offline_text(word)
        else:
            print(f"⚠️ [CHƯA CHẮC CHẮN]: {word} ({c1*100:.1f}%) | Margin: {margin*100:.1f}% | End: {reason}")

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if flip_camera:
                frame = cv2.flip(frame, 1)
            raw_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            raw_rgb.flags.writeable = False
            results = holistic.process(raw_rgb)

            keypoints = extract_keypoints_48(results)
            hands_present = (
                is_active_hand(results.left_hand_landmarks, results.pose_landmarks)
                or is_active_hand(results.right_hand_landmarks, results.pose_landmarks)
            )

            finalized = segmenter.feed(keypoints, hands_present)
            if finalized:
                finalize_word(finalized[0], finalized[1])

            if enable_gui:
                cv2.imshow("Raspberry Pi Edge AI Debug", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    finally:
        pending = segmenter.pending_gesture
        if pending is not None:
            finalize_word(pending, 'shutdown_flush')
        cap.release()
        if enable_gui:
            cv2.destroyAllWindows()
        try:
            holistic.close()
        except Exception:
            pass
        print("🛑 Đã giải phóng an toàn tài nguyên Camera và MediaPipe.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Raspberry Pi Edge AI Sign Language Translator")
    parser.add_argument('--model', type=str, default=DEFAULT_TFLITE_PATH, help="Path to TFLite model")
    parser.add_argument('--show', action='store_true', help="Enable OpenCV Debug Window")
    parser.add_argument('--no_tts', action='store_true', help="Disable Speaker TTS Audio Output")
    parser.add_argument('--flip', action='store_true', default=False, help="Lật gương camera (Mặc định: Tắt để giữ đúng chirality tay)")
    parser.add_argument('--no_flip', action='store_true', default=False, help="Tắt lật gương camera")
    args = parser.parse_args()

    flip_mode = args.flip and not args.no_flip
    run_pi_edge_ai(args.model, enable_gui=args.show, enable_tts=not args.no_tts, flip_camera=flip_mode)
