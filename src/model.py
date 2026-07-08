import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import ModelCheckpoint, TensorBoard, EarlyStopping
from data_loader import get_dataset, get_class_mapping, MAX_FRAMES, NUM_POINTS, NUM_DIMS

# ====== CẤU HÌNH GPU ======
# Chọn GPU rời (GTX 1650) thay vì GPU tích hợp (Intel UHD)
# DirectML liệt kê: GPU:0 = Intel UHD (tích hợp), GPU:1 = GTX 1650 (rời)
gpus = tf.config.list_physical_devices('GPU')
if len(gpus) >= 2:
    # Chỉ sử dụng GPU:1 (GTX 1650)
    try:
        tf.config.set_visible_devices(gpus[1], 'GPU')
        tf.config.experimental.set_memory_growth(gpus[1], True)
        print(f"✅ Đã chọn GPU rời: {gpus[1]}")
    except RuntimeError as e:
        print(f"⚠️ Lỗi cấu hình GPU: {e}")
elif len(gpus) == 1:
    try:
        tf.config.experimental.set_memory_growth(gpus[0], True)
        print(f"✅ Sử dụng GPU duy nhất: {gpus[0]}")
    except RuntimeError as e:
        print(f"⚠️ Lỗi cấu hình GPU: {e}")
else:
    print("⚠️ Không tìm thấy GPU! Sẽ dùng CPU để train.")

# Cấu hình
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(_BASE_DIR, 'models')
LOGS_DIR = os.path.join(_BASE_DIR, 'logs')
BATCH_SIZE = 32
EPOCHS = 3

def build_gru_model(input_shape, num_classes):
    """
    Định nghĩa kiến trúc mô hình GRU cơ bản (Baseline).
    Input shape: (MAX_FRAMES, NUM_POINTS, NUM_DIMS)
    """
    # Vì GRU nhận input 2D cho mỗi frame, ta cần làm phẳng (flatten) tọa độ điểm
    # Chuyển (MAX_FRAMES, NUM_POINTS, NUM_DIMS) -> (MAX_FRAMES, NUM_POINTS * NUM_DIMS)
    flattened_shape = (input_shape[0], input_shape[1] * input_shape[2])
    
    model = Sequential([
        # GRU Layer 1
        GRU(128, return_sequences=True, activation='tanh', input_shape=flattened_shape),
        Dropout(0.2),
        BatchNormalization(),
        
        # GRU Layer 2
        GRU(256, return_sequences=True, activation='tanh'),
        Dropout(0.2),
        BatchNormalization(),
        
        # GRU Layer 3
        GRU(128, return_sequences=False, activation='tanh'),
        Dropout(0.2),
        BatchNormalization(),
        
        # Lớp phân loại cuối cùng
        Dense(128, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
    
    # Sử dụng Sparse Categorical Crossentropy vì nhãn (y) của chúng ta là dạng số (0, 1, 2...)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def reshape_dataset(dataset):
    """Làm phẳng chiều points và dims để đưa vào LSTM"""
    # Chuyển từ (Batch, 60, 76, 3) sang (Batch, 60, 76*3 = 228)
    def reshape_fn(x, y):
        batch_size = tf.shape(x)[0]
        x_reshaped = tf.reshape(x, [batch_size, MAX_FRAMES, NUM_POINTS * NUM_DIMS])
        return x_reshaped, y
    return dataset.map(reshape_fn, num_parallel_calls=tf.data.AUTOTUNE)

def train_model():
    print("Đang chuẩn bị dữ liệu...")
    _, class_names = get_class_mapping()
    num_classes = len(class_names)
    
    # Load dataset
    train_dataset = get_dataset(split='train', batch_size=BATCH_SIZE)
    test_dataset = get_dataset(split='test', batch_size=BATCH_SIZE)
    
    # Định hình lại dữ liệu cho GRU
    train_dataset = reshape_dataset(train_dataset)
    test_dataset = reshape_dataset(test_dataset)
    
    # Khởi tạo mô hình
    print(f"Khởi tạo mô hình GRU cho {num_classes} từ vựng...")
    model = build_gru_model((MAX_FRAMES, NUM_POINTS, NUM_DIMS), num_classes)
    model.summary()
    
    # Thiết lập Callbacks (Lưu mô hình tốt nhất và Early Stopping để chống Overfitting)
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
        
    checkpoint_path = os.path.join(MODELS_DIR, 'vsl_gru_baseline.keras')
    callbacks = [
        ModelCheckpoint(checkpoint_path, monitor='val_accuracy', verbose=1, save_best_only=True, mode='max'),
        EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True),
        TensorBoard(log_dir=LOGS_DIR)
    ]
    
    # Huấn luyện mô hình
    print("Bắt đầu huấn luyện (Training)...")
    history = model.fit(
        train_dataset,
        validation_data=test_dataset,
        epochs=EPOCHS,
        callbacks=callbacks
    )
    print(f"Huấn luyện hoàn tất! Mô hình tốt nhất đã được lưu tại: {checkpoint_path}")

if __name__ == '__main__':
    train_model()
