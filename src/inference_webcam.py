import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import json
import os
import sys

os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from model import build_lstm_model

# Cấu hình đường dẫn
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(_BASE_DIR, 'models', 'vsl_lstm_baseline_colab.keras')
CLASSES_PATH = os.path.join(_BASE_DIR, 'models', 'classes.json')
MAX_FRAMES = 60 # Gom đủ 60 frame (2 giây video) mới đoán 1 lần

# Khởi tạo MediaPipe
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

def extract_keypoints(results):
    # 1. Pose: Lấy 6 điểm cốt lõi (Vai, Khuỷu, Cổ tay)
    if results.pose_landmarks:
        pose_all = np.array([[res.x, res.y, res.z] for res in results.pose_landmarks.landmark])
        pose = pose_all[[11, 12, 13, 14, 15, 16]]
    else:
        pose = np.zeros((6, 3))
        
    if results.left_hand_landmarks:
        lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark])
    else:
        lh = np.zeros((21, 3))
        
    if results.right_hand_landmarks:
        rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark])
    else:
        rh = np.zeros((21, 3))
        
    # Nối lại: 6 + 21 + 21 = 48 điểm
    keypoints = np.concatenate([pose, lh, rh])
    return keypoints

def main():
    print("Đang tải từ điển...")
    try:
        with open(CLASSES_PATH, 'r', encoding='utf-8') as f:
            class_names = json.load(f)
    except Exception as e:
        print(f"Lỗi đọc file classes.json: {e}")
        return

    print("Đang tải bộ não AI (kiến trúc và trọng số), vui lòng chờ vài giây...")
    try:
        # Xây dựng lại kiến trúc mô hình (tương thích Keras 2.15)
        model = build_lstm_model((MAX_FRAMES, 76, 3), len(class_names))
        # Nạp trọng số từ file .keras (đã train trên Colab)
        model.load_weights(MODEL_PATH)
    except Exception as e:
        print(f"Lỗi tải mô hình: {e}")
        return
        
    print("Mở Camera... Vui lòng đứng cách xa camera một chút để AI thấy cả tay và người.")
    cap = cv2.VideoCapture(0)
    
    sequence = []
    sentence = ""
    threshold = 0.8 # Độ tự tin > 80% thì mới tin
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Lật gương cho dễ nhìn
        frame = cv2.flip(frame, 1)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = holistic.process(image)
        
        # Vẽ xương lên màn hình
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        
        # Lấy tọa độ
        keypoints = extract_keypoints(results)
        sequence.append(keypoints)
        
        # Chỉ giữ lại đúng 60 frame gần nhất (cửa sổ trượt)
        sequence = sequence[-MAX_FRAMES:]
        
        # Đủ 60 frame -> Ném vào AI đoán
        if len(sequence) == MAX_FRAMES:
            input_data = np.expand_dims(sequence, axis=0) # shape (1, 60, 76, 3)
            
            res = model.predict(input_data, verbose=0)[0]
            best_idx = np.argmax(res)
            
            if res[best_idx] > threshold:
                predicted_word = class_names[best_idx]
                if sentence != predicted_word:
                    sentence = predicted_word
                    # In tiếng Việt chuẩn ra Terminal
                    print(f"-> AI đoán: {sentence} (Độ tự tin: {res[best_idx]*100:.1f}%)")
                    
        # In chữ không dấu lên màn hình cam (OpenCV không hỗ trợ TV có dấu)
        # Bỏ dấu đi để OpenCV vẽ ko bị lỗi font
        import unicodedata
        ascii_text = unicodedata.normalize('NFKD', sentence).encode('ASCII', 'ignore').decode('utf-8')
        
        # Hiển thị lên cam
        cv2.putText(image, f"Doan: {ascii_text}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        
        cv2.imshow("TEST AI BANG WEBCAM (Bam 'q' de thoat)", image)
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
