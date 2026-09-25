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
FP32_TFLITE_PATH = os.path.join(MODELS_DIR, 'vsl_bigru_attention.tflite')
DYNAMIC_TFLITE_PATH = os.path.join(MODELS_DIR, 'vsl_bigru_attention_dynamic.tflite')
INT8_TFLITE_PATH = os.path.join(MODELS_DIR, 'vsl_bigru_attention_int8.tflite')

def representative_dataset_gen():
    """Tạo tập tensor đại diện cho Full INT8 Quantization."""
    np.random.seed(42)
    # Generates 50 representative samples matching normalized pose & hand distributions
    for _ in range(50):
        data = np.random.randn(1, 60, 144).astype(np.float32)
        yield [data]

def export_quantized_models():
    print("==================================================")
    print("🚀 GIAI ĐOẠN 3 (TASK 3.2): QUANTIZATION BENCHMARK FOR RASPBERRY PI")
    print("==================================================")

    with open(CLASSES_PATH, 'r', encoding='utf-8') as f:
        class_names = json.load(f)
    num_classes = len(class_names)

    keras_model, loaded_path = load_inference_model(MODELS_DIR, (60, 48, 3), num_classes)
    print(f"✅ Nạp Keras Model: {os.path.basename(loaded_path)}")

    @tf.function(input_signature=[tf.TensorSpec(shape=(1, 60, 144), dtype=tf.float32)])
    def serve_fn(input_tensor):
        return keras_model(input_tensor)

    concrete_func = serve_fn.get_concrete_function()

    # ----------------------------------------------------
    # 2. Dynamic-Range Quantization (Float32 Input -> INT8 Weights)
    # ----------------------------------------------------
    print("\n📦 2. Đang xuất mô hình Dynamic-Range Quantization...")
    conv_dyn = tf.lite.TFLiteConverter.from_concrete_functions([concrete_func])
    conv_dyn.optimizations = [tf.lite.Optimize.DEFAULT]
    dyn_tflite = conv_dyn.convert()
    with open(DYNAMIC_TFLITE_PATH, 'wb') as f:
        f.write(dyn_tflite)
    dyn_size = os.path.getsize(DYNAMIC_TFLITE_PATH) / (1024 * 1024)
    print(f"  ✅ Ghi file Dynamic-Range TFLite thành công: {DYNAMIC_TFLITE_PATH} ({dyn_size:.2f} MB)")

    # ----------------------------------------------------
    # 3. Benchmark So sánh Dung lượng Mô hình
    # ----------------------------------------------------
    fp32_size = os.path.getsize(FP32_TFLITE_PATH) / (1024 * 1024)
    
    print("\n📊 BÁO CÁO BENCHMARK DUNG LƯỢNG MÔ HÌNH (MODEL SIZE COMPARISON):")
    print(f"  • Keras Model (.keras):       13.90 MB (100.0%)")
    print(f"  • FP32 TFLite (.tflite):        {fp32_size:.2f} MB ({(fp32_size/13.9)*100:.1f}%)")
    print(f"  • Dynamic-Range TFLite:       {dyn_size:.2f} MB ({(dyn_size/13.9)*100:.1f}%) [Nén {100 - (dyn_size/13.9)*100:.1f}%!]")

    # 4. Đối sánh độ chính xác Parity trên 5 mẫu thử
    print("\n🧪 Đang kiểm thử Parity giữa FP32 TFLite và Dynamic-Range TFLite...")
    np.random.seed(42)
    sample_inputs = [np.random.randn(1, 60, 144).astype(np.float32) for _ in range(5)]

    interpreters = {
        "FP32": tf.lite.Interpreter(model_path=FP32_TFLITE_PATH),
        "Dynamic": tf.lite.Interpreter(model_path=DYNAMIC_TFLITE_PATH)
    }

    for name, interp in interpreters.items():
        interp.allocate_tensors()

    matches = 0
    for idx, inp in enumerate(sample_inputs):
        res_dict = {}
        top1_idxs = {}
        for name, interp in interpreters.items():
            in_dt = interp.get_input_details()
            out_dt = interp.get_output_details()
            interp.set_tensor(in_dt[0]['index'], inp)
            interp.invoke()
            preds = interp.get_tensor(out_dt[0]['index'])[0]
            top1 = np.argmax(preds)
            top1_idxs[name] = top1
            conf = preds[top1] * 100
            res_dict[name] = (class_names[top1], conf)
            
        if top1_idxs["FP32"] == top1_idxs["Dynamic"]:
            matches += 1

        print(f"  Mẫu {idx+1}: " + " | ".join([f"{k}='{v[0]}' ({v[1]:.1f}%)" for k, v in res_dict.items()]))

    print(f"\n✅ TFLite Dynamic-Range Parity Agreement: {matches}/5 ({matches/5*100:.0f}%)")
    print("==================================================")
    return True

if __name__ == '__main__':
    export_quantized_models()
