import cv2
import mediapipe as mp
import numpy as np
import os
import glob
import json
import sys
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

# Global MediaPipe Holistic instance per worker process
_holistic = None

def init_worker():
    global _holistic
    # Khởi tạo MediaPipe Holistic cho từng tiến trình con riêng biệt
    mp_holistic = mp.solutions.holistic
    _holistic = mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

# Cấu hình
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_RAW_DIR = os.path.join(BASE_DIR, 'Dataset', 'raw', 'raw')
OUT_DIR = os.path.join(BASE_DIR, 'data', 'my_preprocessed') # Thư mục lưu kết quả tự làm
NUM_POINTS = 48 # Tối ưu hóa: 21 (Tay trái) + 21 (Tay phải) + 6 (Vai, Khuỷu, Cổ tay) = 48
MAX_FRAMES = 60 # Cố định 60 frames mỗi video
MAX_VIDEOS_PER_CLASS = None # Để None để chạy toàn bộ dataset

def extract_keypoints_48(results):
    """
    Rút trích 48 tọa độ 3D thiết yếu và thực hiện chuẩn hóa (Normalization)
    """
    # 1. Điểm cơ thể (Pose) - Lấy 6 điểm: 11(Vai trái), 12(Vai phải), 13, 14, 15, 16
    pose = np.zeros((6, 3))
    center_x, center_y, center_z = 0.5, 0.5, 0.0 # Default center
    scale = 1.0 # Default scale
    
    if results.pose_landmarks:
        for i, idx in enumerate([11, 12, 13, 14, 15, 16]):
            res = results.pose_landmarks.landmark[idx]
            # Missing-landmark handling: visibility < 0.5 coi như bị mất điểm
            if hasattr(res, 'visibility') and res.visibility > 0.5:
                pose[i] = [res.x, res.y, res.z]
            elif not hasattr(res, 'visibility'):
                pose[i] = [res.x, res.y, res.z]
            else:
                pose[i] = [0.0, 0.0, 0.0]
                
        # Tính tâm 2 vai (11 và 12 tương ứng index 0 và 1 trong mảng pose)
        if not np.array_equal(pose[0], [0.0, 0.0, 0.0]) and not np.array_equal(pose[1], [0.0, 0.0, 0.0]):
            center_x = (pose[0][0] + pose[1][0]) / 2
            center_y = (pose[0][1] + pose[1][1]) / 2
            center_z = (pose[0][2] + pose[1][2]) / 2
            
            # Scale Normalization: Lấy khoảng cách 2 vai làm tỷ lệ
            dist = np.linalg.norm(pose[0] - pose[1])
            if dist > 0.01: # Tránh chia cho 0
                scale = dist

    # 2. Bàn tay trái (Left Hand) - 21 điểm
    lh = np.zeros((21, 3))
    if results.left_hand_landmarks:
        for i, res in enumerate(results.left_hand_landmarks.landmark):
            lh[i] = [res.x, res.y, res.z]
            
    # 3. Bàn tay phải (Right Hand) - 21 điểm
    rh = np.zeros((21, 3))
    if results.right_hand_landmarks:
        for i, res in enumerate(results.right_hand_landmarks.landmark):
            rh[i] = [res.x, res.y, res.z]

    # Nối tất cả lại: 6 + 21 + 21 = 48 điểm
    keypoints = np.concatenate([pose, lh, rh])
    
    # 4. Landmark Normalization (Translation + Scale)
    for i in range(len(keypoints)):
        # Chỉ chuẩn hóa các điểm thực sự tồn tại (khác mảng zeros)
        if not np.array_equal(keypoints[i], [0.0, 0.0, 0.0]):
            keypoints[i][0] = (keypoints[i][0] - center_x) / scale
            keypoints[i][1] = (keypoints[i][1] - center_y) / scale
            keypoints[i][2] = (keypoints[i][2] - center_z) / scale

    return keypoints

def process_video_worker(video_path, save_path):
    """Đọc 1 video mp4 và xuất ra file npy đã qua xử lý (Được gọi song song)"""
    global _holistic
    if _holistic is None:
        init_worker()
        
    if os.path.exists(save_path):
        return "skipped" # Trả về skipped nếu file đã tồn tại trước đó
        
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return "failed"
        
    # Tối ưu hóa: Lấy tổng số frame để lập chỉ mục trích xuất trước
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total_frames <= 0:
        # Dự phòng nếu không đọc được metadata số lượng frames
        frames_data_all = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False 
            results = _holistic.process(image)
            keypoints = extract_keypoints_48(results)
            frames_data_all.append(keypoints)
        cap.release()
        
        if len(frames_data_all) == 0:
            return "failed"
            
        T = len(frames_data_all)
        indices = np.linspace(0, T - 1, MAX_FRAMES, dtype=int)
        resampled_data = [frames_data_all[idx] for idx in indices]
        resampled_data = np.array(resampled_data)
    else:
        # Chỉ mục các frame phân bố đều (Tránh chạy MediaPipe trên toàn bộ frame thừa)
        target_indices = np.linspace(0, total_frames - 1, MAX_FRAMES, dtype=int)
        target_set = set(target_indices)
        
        frames_data = []
        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx in target_set:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False 
                results = _holistic.process(image)
                keypoints = extract_keypoints_48(results)
                frames_data.append(keypoints)
            frame_idx += 1
        cap.release()
        
        if len(frames_data) == 0:
            return "failed"
            
        # Pad thêm zeros nếu số frame thu được thực tế nhỏ hơn 60
        while len(frames_data) < MAX_FRAMES:
            frames_data.append(np.zeros((NUM_POINTS, 3)))
            
        resampled_data = np.array(frames_data[:MAX_FRAMES])
        
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    np.save(save_path, resampled_data)
    return "created" # Trả về created nếu file được tạo mới

def main():
    print("="*60)
    print(" BẮT ĐẦU QUY TRÌNH TIỀN XỬ LÝ SONG SONG NÂNG CAO")
    print(f" 1. Trích xuất 48 điểm (Vai/Khuỷu/Cổ tay + Hai bàn tay)")
    print(f" 2. Landmark Normalization (Translation + Scale)")
    print(f" 3. Temporal Resampling chọn lọc ({MAX_FRAMES} frames)")
    print(f" Lưu tại: {OUT_DIR}")
    print("="*60)
    
    tasks = []
    
    # 1. Thu thập danh sách từ VSL400
    vsl400_dir = os.path.join(DATASET_RAW_DIR, 'VSL400')
    if os.path.exists(vsl400_dir):
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
                if os.path.exists(video_path):
                    save_path = os.path.join(OUT_DIR, gloss, f"vsl400_{video_id}.npy")
                    tasks.append((video_path, save_path))
                    class_counts[gloss] += 1

    # 2. Thu thập danh sách từ online_sourced
    online_dir = os.path.join(DATASET_RAW_DIR, 'online_sourced')
    if os.path.exists(online_dir):
        video_files = glob.glob(os.path.join(online_dir, '*', '*', '*.mp4'))
        class_counts = {}
        for video_path in video_files:
            parts = video_path.split(os.sep)
            gloss = parts[-2]
            if gloss not in class_counts:
                class_counts[gloss] = 0
            if MAX_VIDEOS_PER_CLASS is not None and class_counts[gloss] >= MAX_VIDEOS_PER_CLASS:
                continue
            video_id = parts[-1].replace('.mp4', '')
            save_path = os.path.join(OUT_DIR, gloss, f"online_{video_id}.npy")
            tasks.append((video_path, save_path))
            class_counts[gloss] += 1

    total_tasks = len(tasks)
    print(f"Tổng số lượng video tìm thấy để xử lý: {total_tasks}")
    if total_tasks == 0:
        print("Không tìm thấy video nào. Hãy kiểm tra lại thư mục Dataset/raw/raw/")
        return
        
    # Thiết lập số lượng workers phù hợp (CPU của bạn có 12 logical processors)
    num_workers = min(10, multiprocessing.cpu_count() - 2)
    if num_workers < 1:
        num_workers = 1
    print(f"Khởi chạy song song với {num_workers} tiến trình (workers)...")
    
    completed = 0
    skipped = 0
    success = 0
    failed = 0
    
    with ProcessPoolExecutor(max_workers=num_workers, initializer=init_worker) as executor:
        futures = {executor.submit(process_video_worker, task[0], task[1]): task for task in tasks}
        
        for future in as_completed(futures):
            task = futures[future]
            video_path, save_path = task
            completed += 1
            
            try:
                res = future.result()
                if res == "skipped":
                    skipped += 1
                elif res == "created":
                    success += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                print(f"\n❌ Lỗi khi xử lý file {video_path}: {e}")
                
            # Log tiến độ định kỳ
            if completed % 100 == 0 or completed == total_tasks:
                print(f"Tiến độ: {completed}/{total_tasks} ({completed/total_tasks*100:.1f}%) | "
                      f"Thành công: {success} | Đã có sẵn: {skipped} | Lỗi: {failed}", end='\r')
                sys.stdout.flush()

    print("\n" + "="*50)
    print(" 🎉 HOÀN TẤT TIỀN XỬ LÝ SONG SONG!")
    print(f" - Tổng video: {total_tasks}")
    print(f" - Thành công mới: {success}")
    print(f" - Bỏ qua (Đã xử lý): {skipped}")
    print(f" - Thất bại: {failed}")
    print("="*50)

if __name__ == '__main__':
    # Fix cho multiprocessing trên Windows
    multiprocessing.freeze_support()
    main()
