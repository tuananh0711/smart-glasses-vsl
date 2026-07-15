import os
import shutil
import random
import glob
import sys

# Thiết lập encoding utf-8 cho stdout
sys.stdout.reconfigure(encoding='utf-8')

# Cấu hình
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, 'data', 'my_preprocessed')
DEST_DIR = os.path.join(BASE_DIR, 'data', 'keypoints_splited')
TRAIN_RATIO = 0.8

def main():
    if not os.path.exists(SRC_DIR):
        print(f"Thư mục nguồn không tồn tại: {SRC_DIR}")
        return

    print("="*60)
    print(" BẮT ĐẦU PHÂN CHIA TẬP DỮ LIỆU TRAIN/TEST (Đã tối ưu logic split)")
    print("="*60)

    # Lấy danh sách các class (thư mục con)
    classes = [d for d in os.listdir(SRC_DIR) if os.path.isdir(os.path.join(SRC_DIR, d))]
    print(f"Tổng số từ vựng (classes): {len(classes)}")

    total_train = 0
    total_test = 0

    for idx, cls in enumerate(classes):
        cls_src_dir = os.path.join(SRC_DIR, cls)
        files = glob.glob(os.path.join(cls_src_dir, '*.npy'))
        
        if len(files) == 0:
            continue

        # Shuffle ngẫu nhiên
        random.seed(42) # Đảm bảo tính nhất quán giữa các lần chạy
        random.shuffle(files)

        num_files = len(files)
        # Logic phân chia hợp lý tránh rỗng tập train (Lỗi 4)
        if num_files == 1:
            train_files = files
            test_files = []
        elif num_files == 2:
            train_files = [files[0]]
            test_files = [files[1]]
        else:
            split_idx = int(num_files * TRAIN_RATIO)
            # Đảm bảo có ít nhất 1 file cho test và 1 file cho train
            if split_idx == num_files:
                split_idx = num_files - 1
            if split_idx == 0:
                split_idx = 1
            train_files = files[:split_idx]
            test_files = files[split_idx:]

        # Thư mục đích
        train_dest_dir = os.path.join(DEST_DIR, 'train', cls)
        test_dest_dir = os.path.join(DEST_DIR, 'test', cls)

        # Xóa sạch thư mục đích cũ nếu có để tránh lẫn dữ liệu cũ
        if os.path.exists(train_dest_dir):
            shutil.rmtree(train_dest_dir)
        if os.path.exists(test_dest_dir):
            shutil.rmtree(test_dest_dir)

        os.makedirs(train_dest_dir, exist_ok=True)
        os.makedirs(test_dest_dir, exist_ok=True)

        # Copy files
        for f in train_files:
            shutil.copy2(f, os.path.join(train_dest_dir, os.path.basename(f)))
            total_train += 1

        for f in test_files:
            shutil.copy2(f, os.path.join(test_dest_dir, os.path.basename(f)))
            total_test += 1

        if (idx + 1) % 50 == 0 or (idx + 1) == len(classes):
            print(f"Đã xử lý: {idx + 1}/{len(classes)} classes")

    print("\n" + "="*50)
    print(" 🎉 HOÀN TẤT PHÂN CHIA DỮ LIỆU!")
    print(f" - Tổng số file Train: {total_train}")
    print(f" - Tổng số file Test:  {total_test}")
    print(f" - Lưu tại: {DEST_DIR}")
    print("="*50)

if __name__ == '__main__':
    main()
