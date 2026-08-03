import os
import sys
import json
import time
import numpy as np
import tensorflow as tf

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from model_loader import load_inference_model

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(_BASE_DIR, 'models')
CLASSES_PATH = os.path.join(MODELS_DIR, 'classes.json')
TFLITE_PATH = os.path.join(MODELS_DIR, 'vsl_bigru_attention.tflite')

def verify_tflite_parity():
    print("==================================================")
    print("🔍 GIAI ĐOẠN 3: KIỂM THỬ ĐỐI SÁNH KẾT QUẢ KERAS VS TFLITE")
    print("==================================================")

    # 1. Đọc từ điển
    with open(CLASSES_PATH, 'r', encoding='utf-8') as f:
        class_names = json.load(f)
    num_classes = len(class_names)

    # 2. Nạp mô hình Keras
    keras_model, loaded_path = load_inference_model(MODELS_DIR, (60, 48, 3), num_classes)
    print(f"✅ Nạp Keras Model: {os.path.basename(loaded_path)}")

    # 3. Nạp mô hình TFLite
    if not os.path.exists(TFLITE_PATH):
        print(f"❌ Không tìm thấy file TFLite: {TFLITE_PATH}")
        return False

    interpreter = tf.lite.Interpreter(model_path=TFLITE_PATH)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print(f"✅ Nạp TFLite Model: {os.path.basename(TFLITE_PATH)} ({os.path.getsize(TFLITE_PATH)/(1024*1024):.2f} MB)")

    # 4. Tạo 5 mẫu ngẫu nhiên (Dummy Tensors) để đo sai số & độ trễ
    np.random.seed(42)
    sample_inputs = [np.random.randn(1, 60, 144).astype(np.float32) for _ in range(5)]

    keras_times = []
    tflite_times = []
    max_diffs = []
    matches = 0

    print("\n🧪 Đang chạy suy luận thử nghiệm trên 5 mẫu dữ liệu...")
    for i, dummy_input in enumerate(sample_inputs):
        # Keras Inference
        t0 = time.perf_counter()
        keras_preds = keras_model.predict(dummy_input, verbose=0)[0]
        t1 = time.perf_counter()
        keras_times.append((t1 - t0) * 1000)

        # TFLite Inference
        t2 = time.perf_counter()
        interpreter.set_tensor(input_details[0]['index'], dummy_input)
        interpreter.invoke()
        tflite_preds = interpreter.get_tensor(output_details[0]['index'])[0]
        t3 = time.perf_counter()
        tflite_times.append((t3 - t2) * 1000)

        # Top 1
        k_top1 = np.argmax(keras_preds)
        t_top1 = np.argmax(tflite_preds)
        max_diff = np.max(np.abs(keras_preds - tflite_preds))
        max_diffs.append(max_diff)

        if k_top1 == t_top1:
            matches += 1

        print(f"  Mẫu {i+1}: Keras Top1='{class_names[k_top1]}' ({keras_preds[k_top1]*100:.2f}%) | "
              f"TFLite Top1='{class_names[t_top1]}' ({tflite_preds[t_top1]*100:.2f}%) | "
              f"Diff Max={max_diff:.6f}")

    avg_k_time = np.mean(keras_times)
    avg_t_time = np.mean(tflite_times)
    avg_diff = np.mean(max_diffs)

    print("\n📊 BÁO CÁO NGHIỆM THU ĐỐI SÁNH TFLITE PARITY:")
    print(f"  • Top-1 Agreement Rate: {matches}/5 ({matches/5*100:.0f}%)")
    print(f"  • Max Absolute Difference: {np.max(max_diffs):.6f}")
    print(f"  • Thời gian suy luận trung bình trên PC:")
    print(f"    - Keras Model:  {avg_k_time:.2f} ms")
    print(f"    - TFLite Model: {avg_t_time:.2f} ms (Nhanh hơn {avg_k_time/avg_t_time:.1f}x)")
    print("==================================================")
    return True

if __name__ == '__main__':
    verify_tflite_parity()
