"""Script test chạy 3 epochs để đo thời gian training trên GPU (DirectML)."""
import os
import sys
import time

# ====== CHỌN GPU RỜI TRƯỚC KHI IMPORT TENSORFLOW ======
os.environ['DML_VISIBLE_DEVICES'] = '1'
# Tắt CuDNN vì DirectML không hỗ trợ
os.environ['TF_CUDNN_USE_AUTOTUNE'] = '0'

sys.stdout.reconfigure(encoding='utf-8')

import tensorflow as tf
import numpy as np

gpus = tf.config.list_physical_devices('GPU')
print(f"GPU khả dụng: {gpus}")
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
    print(f"✅ Đã cấu hình {len(gpus)} GPU với memory growth")
else:
    print("⚠️ Không tìm thấy GPU! Dùng CPU.")

from data_loader import get_dataset, get_class_mapping, MAX_FRAMES, NUM_POINTS, NUM_DIMS
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization

TEST_EPOCHS = 3
BATCH_SIZE = 32

def build_model(input_shape, num_classes):
    """
    Build LSTM model tương thích với DirectML.
    Thêm recurrent_dropout nhỏ (1e-5) để ép TF dùng generic kernel 
    thay vì CuDNN kernel (không được hỗ trợ trên DirectML).
    """
    flattened_shape = (input_shape[0], input_shape[1] * input_shape[2])
    model = Sequential([
        # LSTM Layer 1 - thêm recurrent_dropout để tránh CuDNN
        LSTM(128, return_sequences=True, activation='tanh', 
             input_shape=flattened_shape, recurrent_dropout=1e-5),
        Dropout(0.2),
        BatchNormalization(),
        # LSTM Layer 2
        LSTM(256, return_sequences=True, activation='tanh',
             recurrent_dropout=1e-5),
        Dropout(0.2),
        BatchNormalization(),
        # LSTM Layer 3
        LSTM(128, return_sequences=False, activation='tanh',
             recurrent_dropout=1e-5),
        Dropout(0.2),
        BatchNormalization(),
        # Dense layers
        Dense(128, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model

def reshape_ds(dataset):
    """Reshape dataset cho LSTM."""
    def reshape_fn(x, y):
        batch_size = tf.shape(x)[0]
        x_reshaped = tf.reshape(x, [batch_size, MAX_FRAMES, NUM_POINTS * NUM_DIMS])
        return x_reshaped, y
    return dataset.map(reshape_fn, num_parallel_calls=tf.data.AUTOTUNE)

def main():
    print("=" * 60)
    print("🧪 TEST TRAINING - 3 EPOCHS trên GTX 1650 (DirectML)")
    print("=" * 60)
    
    # Load data
    print("\n📦 Đang load dữ liệu...")
    _, class_names = get_class_mapping()
    num_classes = len(class_names)
    print(f"   Số classes: {num_classes}")
    
    train_dataset = get_dataset(split='train', batch_size=BATCH_SIZE)
    test_dataset = get_dataset(split='test', batch_size=BATCH_SIZE)
    
    train_dataset = reshape_ds(train_dataset)
    test_dataset = reshape_ds(test_dataset)
    
    # Build model
    print(f"\n🏗️ Khởi tạo mô hình LSTM (DirectML compatible)...")
    model = build_model((MAX_FRAMES, NUM_POINTS, NUM_DIMS), num_classes)
    total_params = model.count_params()
    print(f"   Tổng parameters: {total_params:,}")
    
    # Train
    print(f"\n🚀 Bắt đầu training {TEST_EPOCHS} epochs...")
    print("-" * 60)
    
    start_total = time.time()
    
    history = model.fit(
        train_dataset,
        validation_data=test_dataset,
        epochs=TEST_EPOCHS,
        verbose=1
    )
    
    total_time = time.time() - start_total
    avg_time_per_epoch = total_time / TEST_EPOCHS
    
    # Kết quả
    print("\n" + "=" * 60)
    print("📊 KẾT QUẢ TEST")
    print("=" * 60)
    print(f"   Tổng thời gian {TEST_EPOCHS} epochs: {total_time:.1f}s ({total_time/60:.1f} phút)")
    print(f"   Trung bình mỗi epoch:            {avg_time_per_epoch:.1f}s")
    print(f"   Train accuracy (epoch cuối):      {history.history['accuracy'][-1]*100:.2f}%")
    print(f"   Val accuracy (epoch cuối):        {history.history['val_accuracy'][-1]*100:.2f}%")
    print(f"   Train loss (epoch cuối):          {history.history['loss'][-1]:.4f}")
    print(f"   Val loss (epoch cuối):            {history.history['val_loss'][-1]:.4f}")
    
    # Lưu mô hình test tương thích để chạy inference test (Lỗi 2)
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
    os.makedirs(models_dir, exist_ok=True)
    model_save_path = os.path.join(models_dir, 'vsl_lstm_baseline_colab.keras')
    model.save(model_save_path)
    print(f"💾 Đã lưu mô hình test tại: {model_save_path}")
    
    # Ước tính 100 epochs
    est_100 = avg_time_per_epoch * 100
    print(f"\n⏱️ DỰ TÍNH CHO 100 EPOCHS:")
    print(f"   Ước tính: {est_100:.0f}s = {est_100/60:.0f} phút = {est_100/3600:.1f} giờ")
    print(f"   (Có EarlyStopping nên thực tế có thể ngắn hơn)")
    print("=" * 60)

if __name__ == '__main__':
    main()
