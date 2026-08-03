import os
import sys
import json
import numpy as np
import tensorflow as tf

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from model_loader import load_inference_model

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(_BASE_DIR, 'models')
CLASSES_PATH = os.path.join(MODELS_DIR, 'classes.json')
OUTPUT_TFLITE_PATH = os.path.join(MODELS_DIR, 'vsl_bigru_attention.tflite')

def export_tflite():
    print("==================================================")
    print("🚀 GIAI ĐOẠN 3: XUẤT MÔ HÌNH SANG TENSORFLOW LITE (FP32)")
    print("==================================================")

    # 1. Đọc từ điển số lượng lớp
    try:
        with open(CLASSES_PATH, 'r', encoding='utf-8') as f:
            class_names = json.load(f)
        num_classes = len(class_names)
        print(f"✅ Đã nạp từ điển: {num_classes} từ vựng.")
    except Exception as e:
        print(f"❌ Lỗi nạp classes.json: {e}")
        return False

    # 2. Nạp mô hình Keras checkpoint
    input_shape = (60, 48, 3)
    try:
        keras_model, loaded_path = load_inference_model(MODELS_DIR, input_shape, num_classes)
        print(f"✅ Nạp thành công Keras model: {os.path.basename(loaded_path)}")
    except Exception as e:
        print(f"❌ Lỗi nạp Keras model: {e}")
        return False

    # 3. Tạo TFLite Converter thông qua Concrete Function
    print("\n📦 Bắt đầu chuyển đổi Keras -> TFLite (FP32)...")
    
    @tf.function(input_signature=[tf.TensorSpec(shape=(1, 60, 144), dtype=tf.float32)])
    def serve_fn(input_tensor):
        return keras_model(input_tensor)

    concrete_func = serve_fn.get_concrete_function()
    converter = tf.lite.TFLiteConverter.from_concrete_functions([concrete_func])
    converter.optimizations = []
    
    try:
        tflite_model = converter.convert()
        print("✅ Chuyển đổi TFLite Graph thành công!")
    except Exception as e:
        print(f"⚠️ Chuyển đổi mặc định thất bại, thử bật Select TF Ops: {e}")
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS,
            tf.lite.OpsSet.SELECT_TF_OPS
        ]
        tflite_model = converter.convert()
        print("✅ Chuyển đổi TFLite với Select TF Ops thành công!")

    # 4. Ghi file .tflite
    with open(OUTPUT_TFLITE_PATH, 'wb') as f:
        f.write(tflite_model)
    
    size_mb = os.path.getsize(OUTPUT_TFLITE_PATH) / (1024 * 1024)
    print(f"🎉 Ghi thành công file TFLite: {OUTPUT_TFLITE_PATH}")
    print(f"📊 Kích thước file TFLite FP32: {size_mb:.2f} MB")

    # 5. Kiểm tra Signature và Tensors
    interpreter = tf.lite.Interpreter(model_path=OUTPUT_TFLITE_PATH)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print("\n🔍 THÔNG SỐ TENSOR TFLITE MODEL:")
    print(f"  • Input Shape: {input_details[0]['shape']} ({input_details[0]['dtype']})")
    print(f"  • Output Shape: {output_details[0]['shape']} ({output_details[0]['dtype']})")
    print("==================================================")
    return True

if __name__ == '__main__':
    export_tflite()
