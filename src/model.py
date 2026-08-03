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

def build_lstm_model(input_shape, num_classes):
    """
    Xây dựng mô hình LSTM tương ứng với file weights lstm nếu được nạp.
    """
    if len(input_shape) == 2:
        flattened_shape = input_shape
    else:
        flattened_shape = (input_shape[0], input_shape[1] * input_shape[2])
        
    model = Sequential([
        tf.keras.layers.LSTM(128, return_sequences=True, activation='tanh', input_shape=flattened_shape),
        Dropout(0.2),
        BatchNormalization(),
        tf.keras.layers.LSTM(256, return_sequences=True, activation='tanh'),
        Dropout(0.2),
        BatchNormalization(),
        tf.keras.layers.LSTM(128, return_sequences=False, activation='tanh'),
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

def build_bigru_attention_model(input_shape, num_classes):
    """
    Định nghĩa kiến trúc mô hình nâng cấp: Bidirectional GRU + Multi-Head Self-Attention.
    Giúp học quan hệ 2 chiều thời gian và tập trung vào các khung hình chứa cử chỉ bàn tay quan trọng.
    Input shape: (MAX_FRAMES, NUM_POINTS, NUM_DIMS) hoặc (MAX_FRAMES, NUM_POINTS * NUM_DIMS)
    """
    if len(input_shape) == 2:
        flattened_shape = input_shape
    else:
        flattened_shape = (input_shape[0], input_shape[1] * input_shape[2])

    inputs = tf.keras.Input(shape=flattened_shape)
    
    # 1. Feature Projection & Embedding
    x = tf.keras.layers.Dense(256, activation='relu')(inputs)
    x = tf.keras.layers.LayerNormalization()(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    
    # 2. Bidirectional GRU Layer 1
    x = tf.keras.layers.Bidirectional(tf.keras.layers.GRU(128, return_sequences=True))(x)
    x = tf.keras.layers.LayerNormalization()(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    
    # 3. Bidirectional GRU Layer 2
    x = tf.keras.layers.Bidirectional(tf.keras.layers.GRU(128, return_sequences=True))(x)
    x = tf.keras.layers.LayerNormalization()(x)
    
    # 4. Multi-Head Self-Attention Layer (Tập trung vào các frame chứa nét ký hiệu trọng tâm)
    attention_output = tf.keras.layers.MultiHeadAttention(num_heads=4, key_dim=64)(x, x)
    x = tf.keras.layers.Add()([x, attention_output])
    x = tf.keras.layers.LayerNormalization()(x)
    
    # 5. Global Temporal Pooling (Hợp nhất Pooling Trung bình và Pooling Cực đại)
    avg_pool = tf.keras.layers.GlobalAveragePooling1D()(x)
    max_pool = tf.keras.layers.GlobalMaxPooling1D()(x)
    pooled = tf.keras.layers.Concatenate()([avg_pool, max_pool])
    
    # 6. Classifier Head
    x = tf.keras.layers.Dense(256, activation='relu')(pooled)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation='softmax')(x)
    
    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="VSL_BiGRU_Attention")
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def build_gru_model(input_shape, num_classes):
    """
    Định nghĩa kiến trúc mô hình GRU 3 lớp cơ bản (Baseline).
    Giữ nguyên tương thích tuyệt đối với tập trọng số cũ vsl_gru_baseline.h5.
    """
    if len(input_shape) == 2:
        flattened_shape = input_shape
    else:
        flattened_shape = (input_shape[0], input_shape[1] * input_shape[2])
    
    model = Sequential([
        GRU(128, return_sequences=True, activation='tanh', input_shape=flattened_shape),
        Dropout(0.2),
        BatchNormalization(),
        
        GRU(256, return_sequences=True, activation='tanh'),
        Dropout(0.2),
        BatchNormalization(),
        
        GRU(128, return_sequences=False, activation='tanh'),
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
