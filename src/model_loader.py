import os
import numpy as np
from model import build_gru_model, build_lstm_model, build_bigru_attention_model

def load_inference_model(models_dir, input_shape, num_classes):
    """
    Tải mô hình tốt nhất có sẵn trong thư mục models_dir bằng phương pháp thử tuần tự.
    Luôn thử load_weights trên builder_fn tương ứng.
    Thực hiện smoke test (forward pass với dummy input) để đảm bảo mô hình thực sự hoạt động.
    """
    candidates = [
        ("vsl_bigru_attention_colab.keras", build_bigru_attention_model),
        ("vsl_bigru_attention.keras", build_bigru_attention_model),
        ("vsl_bigru_attention.h5", build_bigru_attention_model),
        ("vsl_gru_baseline.h5", build_gru_model),
        ("vsl_gru_baseline.keras", build_gru_model),
        ("vsl_gru_baseline_colab.keras", build_gru_model),
    ]
    errors = []
    
    for filename, builder in candidates:
        path = os.path.join(models_dir, filename)
        if not os.path.exists(path):
            continue
            
        try:
            # Dựng kiến trúc
            candidate = builder(input_shape, num_classes)
            # Nạp trọng số
            candidate.load_weights(path)
            
            # Smoke test
            dummy = np.zeros(
                (1, input_shape[0], input_shape[1] * input_shape[2]),
                dtype=np.float32,
            )
            output = candidate(dummy, training=False).numpy()
            
            if output.shape != (1, num_classes) or not np.isfinite(output).all():
                raise ValueError(f"Invalid smoke output: {output.shape}")
                
            return candidate, path
        except Exception as exc:
            errors.append(f"{filename}: {exc}")
            
    raise RuntimeError("No compatible checkpoint found:\\n" + "\\n".join(errors))
