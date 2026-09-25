import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import glob
import numpy as np
import tensorflow as tf

# Cấu hình hằng số
# Sử dụng đường dẫn tuyệt đối dựa trên vị trí file để tránh lỗi khi chạy từ thư mục khác
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(_BASE_DIR, 'data', 'keypoints_splited')
MAX_FRAMES = 60 # Số lượng frame tối đa (Padding/Truncating)
NUM_POINTS = 48 # Số khớp theo cấu hình rút gọn (Pose 6 + Left 21 + Right 21)
NUM_DIMS = 3 # Tọa độ X, Y, Z
CLASSES_FILE = os.path.join(_BASE_DIR, 'data', 'classes.json')

def get_class_mapping():
    """Lấy danh sách các nhãn (classes) và tạo mapping sang số."""
    # Lấy danh sách các thư mục con trong thư mục train để làm danh sách class
    train_dir = os.path.join(DATA_DIR, 'train')
    
    # Lấy tên các thư mục (class names) và sắp xếp theo thứ tự alphabet
    class_names = sorted([d for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, d))])
    
    # Lưu lại file classes.json để sau này dùng cho việc dự đoán (inference)
    if not os.path.exists(os.path.dirname(CLASSES_FILE)):
        os.makedirs(os.path.dirname(CLASSES_FILE))
        
    with open(CLASSES_FILE, 'w', encoding='utf-8') as f:
        json.dump(class_names, f, ensure_ascii=False, indent=4)
        
    class_to_id = {name: idx for idx, name in enumerate(class_names)}
    return class_to_id, class_names

def pad_or_truncate(data, max_frames):
    """
    Chuẩn hóa số lượng frame.
    - Nếu frame ít hơn max_frames -> Thêm các frame toàn số 0 (Padding).
    - Nếu frame nhiều hơn max_frames -> Cắt bỏ phần dư (Truncating).
    """
    t = data.shape[0]
    if t > max_frames:
        # Cắt bớt (có thể cắt ở đuôi)
        return data[:max_frames, :, :]
    elif t < max_frames:
        # Pad thêm số 0
        pad_size = max_frames - t
        padding = np.zeros((pad_size, NUM_POINTS, NUM_DIMS), dtype=np.float32)
        return np.vstack([data, padding])
    else:
        return data

def data_generator(split='train'):
    """Generator để đọc từng file .npy và sinh ra (dữ liệu, nhãn)."""
    class_to_id, _ = get_class_mapping()
    split_dir = os.path.join(DATA_DIR, split)
    
    # Dùng glob để tìm tất cả các file .npy
    pattern = os.path.join(split_dir, '*', '*.npy')
    files = glob.glob(pattern)
    
    # Xáo trộn file nếu là tập train
    if split == 'train':
        np.random.shuffle(files)
        
    for file_path in files:
        try:
            # Tên thư mục chứa file chính là tên nhãn (class)
            class_name = os.path.basename(os.path.dirname(file_path))
            label_id = class_to_id[class_name]
            
            # Đọc dữ liệu từ file .npy
            data = np.load(file_path).astype(np.float32)
            
            # Chuẩn hóa kích thước
            data = pad_or_truncate(data, MAX_FRAMES)
            
            yield data, label_id
            
        except Exception as e:
            print(f"Lỗi khi đọc file {file_path}: {e}")
            continue

def get_dataset(split='train', batch_size=32):
    """
    Tạo tf.data.Dataset sẵn sàng cho việc huấn luyện mô hình TensorFlow.
    """
    dataset = tf.data.Dataset.from_generator(
        lambda: data_generator(split=split),
        output_signature=(
            tf.TensorSpec(shape=(MAX_FRAMES, NUM_POINTS, NUM_DIMS), dtype=tf.float32),
            tf.TensorSpec(shape=(), dtype=tf.int32)
        )
    )
    
    if split == 'train':
        # Chỉ shuffle bộ nhớ đệm (buffer) cho generator
        dataset = dataset.shuffle(buffer_size=500)
        
    dataset = dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    return dataset

if __name__ == '__main__':
    # Chạy thử code để kiểm tra
    print("Đang khởi tạo Data Loader...")
    class_to_id, class_names = get_class_mapping()
    print(f"Tổng số từ vựng (Classes): {len(class_names)}")
    
    train_dataset = get_dataset(split='train', batch_size=32)
    print("\nLấy thử 1 Batch từ tập Train:")
    for data, labels in train_dataset.take(1):
        print(f"Kích thước X_batch: {data.shape} -> (Batch Size, Frames, Points, Dims)")
        print(f"Kích thước y_batch: {labels.shape}")
        break
    print("\nHoàn tất kiểm tra Data Loader!")
