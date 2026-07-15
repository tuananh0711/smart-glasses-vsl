import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import json
import os
import sys
import glob

os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from model import build_gru_model

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

def build_lstm_model(input_shape, num_classes):
    """Xây dựng mô hình LSTM tương ứng với file weights lstm nếu được nạp"""
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
    flattened_shape = (input_shape[0], input_shape[1] * input_shape[2])
    model = Sequential([
        LSTM(128, return_sequences=True, activation='tanh', input_shape=flattened_shape),
        Dropout(0.2),
        BatchNormalization(),
        LSTM(256, return_sequences=True, activation='tanh'),
        Dropout(0.2),
        BatchNormalization(),
        LSTM(128, return_sequences=False, activation='tanh'),
        Dropout(0.2),
        BatchNormalization(),
        Dense(128, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

def main():
    print("Đang tải từ điển...")
    try:
        with open(CLASSES_PATH, 'r', encoding='utf-8') as f:
            class_names = json.load(f)
    except Exception as e:
        print(f"Lỗi đọc file classes.json: {e}")
        return

    print("Đang tải bộ não AI (GRU/LSTM 48 điểm)...")
    try:
        model_file = None
        # Kiểm tra file mặc định vsl_gru_baseline.keras
        if os.path.exists(MODEL_PATH):
            model_file = MODEL_PATH
        else:
            # Nếu không tìm thấy, quét thư mục models để tìm file weights khả dụng khác
            models_dir = os.path.dirname(MODEL_PATH)
            candidate_files = glob.glob(os.path.join(models_dir, '*.keras'))
            if candidate_files:
                model_file = candidate_files[0]
                print(f"👉 Không tìm thấy {MODEL_PATH}, sử dụng file weights: {model_file}")

        if model_file:
            base_name = os.path.basename(model_file).lower()
            if "lstm" in base_name:
                print("🧠 Dựng mô hình kiến trúc LSTM...")
                model = build_lstm_model((MAX_FRAMES, NUM_POINTS, NUM_DIMS), len(class_names))
            else:
                print("🧠 Dựng mô hình kiến trúc GRU...")
                model = build_gru_model((MAX_FRAMES, NUM_POINTS, NUM_DIMS), len(class_names))
                
            model.load_weights(model_file)
            print("✅ Đã nạp trọng số thành công!")
        else:
            print(f"⚠️ Chưa có file weights tại {MODEL_PATH}.")
            print("Sẽ chạy với mô hình GRU ngẫu nhiên để test luồng dữ liệu.")
            model = build_gru_model((MAX_FRAMES, NUM_POINTS, NUM_DIMS), len(class_names))
    except Exception as e:
        print(f"Lỗi tải mô hình: {e}")
        return
        
    print("Mở Camera... (Sẵn sàng Picamera2 cho Raspberry Pi)")
    cap = cv2.VideoCapture(0)
    
    sequence = []
    sentence_list = []
    current_word = ""
    debounce_counter = 0
    hands_down_counter = 0
    
    # Cấu hình bộ lọc
    CONFIDENCE_THRESHOLD = 0.85
    DEBOUNCE_FRAMES = 5
    HANDS_DOWN_FRAMES = 15 # Nếu 15 frame liên tiếp buông tay -> Ngắt câu
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = holistic.process(image)
        
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
        
        keypoints = extract_keypoints_48(results)
        sequence.append(keypoints)
        
        # Cửa sổ trượt (Sliding Window)
        sequence = sequence[-MAX_FRAMES:]
        
        # Kiểm tra Sentence Boundary (Ngắt câu)
        is_hands_down = not results.left_hand_landmarks and not results.right_hand_landmarks
        if is_hands_down:
            hands_down_counter += 1
        else:
            hands_down_counter = 0
            
        if hands_down_counter >= HANDS_DOWN_FRAMES:
            if current_word != "":
                current_word = "" # Reset từ hiện tại để có thể lặp lại ở câu mới
                # print("-> [NGẮT CÂU]")
            
        # Dự đoán
        if len(sequence) == MAX_FRAMES:
            # Định hình đầu vào cho mạng GRU: (Batch, MAX_FRAMES, 144)
            input_data = np.expand_dims(sequence, axis=0)
            input_data = np.reshape(input_data, (1, MAX_FRAMES, NUM_POINTS * NUM_DIMS))
            
            res = model.predict(input_data, verbose=0)[0]
            best_idx = np.argmax(res)
            confidence = res[best_idx]
            
            # 1. Confidence Filter
            if confidence > CONFIDENCE_THRESHOLD:
                predicted_word = class_names[best_idx]
                
                # 2. Debounce Filter (Chống nhiễu lặp từ)
                if predicted_word == current_word:
                    debounce_counter += 1
                else:
                    current_word = predicted_word
                    debounce_counter = 1
                    
                # 3. Thêm vào câu nếu từ đủ ổn định
                if debounce_counter == DEBOUNCE_FRAMES:
                    if len(sentence_list) == 0 or sentence_list[-1] != current_word:
                        sentence_list.append(current_word)
                        print(f"-> Thêm từ: {current_word} ({confidence*100:.1f}%)")
                        
        # Giao diện hiển thị
        import unicodedata
        # Hiển thị 5 từ gần nhất trên camera
        display_sentence = " ".join(sentence_list[-5:]) 
        ascii_text = unicodedata.normalize('NFKD', display_sentence).encode('ASCII', 'ignore').decode('utf-8')
        
        cv2.putText(image, f"Cau: {ascii_text}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        
        cv2.imshow("TEST AI KINH THONG MINH", image)
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
