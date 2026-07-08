import cv2
import mediapipe as mp
import numpy as np
import os
import glob
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Khởi tạo MediaPipe Holistic
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Cấu hình
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_RAW_DIR = os.path.join(BASE_DIR, 'Dataset', 'raw', 'raw')
OUT_DIR = os.path.join(BASE_DIR, 'data', 'my_preprocessed') # Thư mục lưu kết quả tự làm
NUM_POINTS = 48 # Tối ưu hóa: 21 (Tay trái) + 21 (Tay phải) + 6 (Vai, Khuỷu, Cổ tay) = 48
MAX_VIDEOS_PER_CLASS = 10 # Chỉ chạy 10 video mỗi từ để làm minh chứng báo cáo

def extract_keypoints_48(results):
    """
    Rút trích chính xác 48 tọa độ 3D thiết yếu từ kết quả của MediaPipe.
    Loại bỏ đầu/mặt và thân dưới để giảm nhiễu và tối ưu tốc độ cho Pi.
    """
    # 1. Điểm cơ thể (Pose) - Lấy 6 điểm: 11 (Vai trái), 12 (Vai phải), 13, 14, 15, 16
    if results.pose_landmarks:
        pose_all = np.array([[res.x, res.y, res.z] for res in results.pose_landmarks.landmark])
        # Lấy chính xác các index 11->16
        pose = pose_all[[11, 12, 13, 14, 15, 16]]
    else:
        pose = np.zeros((6, 3))
        
    # 2. Bàn tay trái (Left Hand) - 21 điểm
    if results.left_hand_landmarks:
        lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark])
    else:
        lh = np.zeros((21, 3))
        
    # 3. Bàn tay phải (Right Hand) - 21 điểm
    if results.right_hand_landmarks:
        rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark])
    else:
        rh = np.zeros((21, 3))
        
    # Nối tất cả lại: 6 + 21 + 21 = 48 điểm
    keypoints = np.concatenate([pose, lh, rh])
    return keypoints

def process_video(video_path, save_path):
    """Đọc 1 video mp4 và xuất ra file npy"""
    if os.path.exists(save_path):
        return True # Bỏ qua nếu đã chạy rồi
        
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return False
        
    frames_data = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False 
        results = holistic.process(image)
        
        keypoints = extract_keypoints_48(results)
        frames_data.append(keypoints)
        
    cap.release()
    
    if len(frames_data) == 0:
        return False
        
    npy_data = np.array(frames_data)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    np.save(save_path, npy_data)
    return True

def process_vsl400():
    print(">>> Bắt đầu xử lý tập VSL400...")
    vsl400_dir = os.path.join(DATASET_RAW_DIR, 'VSL400')
    if not os.path.exists(vsl400_dir):
        print(f"Không tìm thấy thư mục: {vsl400_dir}")
        return
        
    # Tìm tất cả file front_view.json
    json_files = glob.glob(os.path.join(vsl400_dir, 'Part_*', 'split_*', 'front_view.json'))
    class_counts = {}
    
    for json_file in json_files:
        base_path = os.path.dirname(json_file)
        video_dir = os.path.join(base_path, 'front_view')
        
        with open(json_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        for item in metadata:
            gloss = item.get('gloss')
            video_id = item.get('video_id')
            
            if gloss not in class_counts:
                class_counts[gloss] = 0
                
            if MAX_VIDEOS_PER_CLASS is not None and class_counts[gloss] >= MAX_VIDEOS_PER_CLASS:
                continue
                
            video_path = os.path.join(video_dir, f"{video_id}.mp4")
            if not os.path.exists(video_path):
                continue
                
            save_path = os.path.join(OUT_DIR, gloss, f"vsl400_{video_id}.npy")
            if process_video(video_path, save_path):
                class_counts[gloss] += 1
                print(f"[VSL400] Đã xử lý: {gloss} ({class_counts[gloss]}/{MAX_VIDEOS_PER_CLASS or '∞'})")

def process_online_sourced():
    print("\n>>> Bắt đầu xử lý tập online_sourced...")
    online_dir = os.path.join(DATASET_RAW_DIR, 'online_sourced')
    if not os.path.exists(online_dir):
        print(f"Không tìm thấy thư mục: {online_dir}")
        return
        
    # Cấu trúc: online_sourced/{train,test}/{gloss}/{video_id}.mp4
    video_files = glob.glob(os.path.join(online_dir, '*', '*', '*.mp4'))
    class_counts = {}
    
    for video_path in video_files:
        parts = video_path.split(os.sep)
        gloss = parts[-2]
        video_id = parts[-1].replace('.mp4', '')
        
        if gloss not in class_counts:
            class_counts[gloss] = 0
            
        if MAX_VIDEOS_PER_CLASS is not None and class_counts[gloss] >= MAX_VIDEOS_PER_CLASS:
            continue
            
        save_path = os.path.join(OUT_DIR, gloss, f"online_{video_id}.npy")
        if process_video(video_path, save_path):
            class_counts[gloss] += 1
            print(f"[Online] Đã xử lý: {gloss} ({class_counts[gloss]}/{MAX_VIDEOS_PER_CLASS or '∞'})")

def main():
    print("="*50)
    print(" BẮT ĐẦU QUY TRÌNH TIỀN XỬ LÝ 48 POINTS (ON-DEVICE)")
    print(f" Lọc đúng 6 điểm vai/khuỷu/cổ tay + 42 điểm bàn tay")
    print(f" Lưu tại: {OUT_DIR}")
    print("="*50)
    
    process_vsl400()
    process_online_sourced()
    
    print("\n🎉 Hoàn tất tiền xử lý!")

if __name__ == '__main__':
    main()
