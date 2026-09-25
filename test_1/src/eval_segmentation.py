"""
eval_segmentation.py — Benchmark e2e cho machine phân đoạn 4 pha.

Bối cảnh (qc_report.md Kỳ 2): phiên bản cũ mô phỏng state machine trên các file
`.npy` ĐÃ được `preprocess.py` resample sẵn về 60 frame. Vì vậy kịch bản "State
Machine cap 100" ≡ kịch bản "whole sample 60 frame" (đồng nhất thức) và KHI
CHƯA BAO GIỜ chạy qua state machine thật, camera, ARMING hay bloat. Con số
82.49%/+31.15 điểm không có giá trị kiểm chứng đường live.

Bản này sửa bằng cách:
  1. Đọc VIDEO GỐC từ Dataset (frame-by-frame, đúng như webcam).
  2. Chạy ĐÚNG `segmentation.Segmenter` production (không copy-paste logic).
  3. Thêm các kịch bản mà bản cũ không có:
       - whole-clip  : trần trên (không phân đoạn) = upper bound.
       - clean       : máy trạng thái trên clip chuẩn (cuối clip người ký hạ tay).
       - BLOAT       : người ký GIỮ TAY IM sau khi ký (không hạ) -> kịch bản
                       xảy ra liên tục trên webcam thật nhưng không có trong
                       video studio, chính là lý do TASK-013 hết lỗi 3.4% mà
                       live vẫn tệ.
       - FLIP        : lật ngang landmark để định lượng nhạy cảm chirality.
  4. Kịch bản `intrinsic-npy` GIỮ LẠI nhưng đặt tên rõ là "độ chính xác vốn có
     của model", KHÔNG phải pipeline.

ADR-001: script chạy offline hoàn toàn, không network.
"""

import os
import sys
import json
import glob
import random
import argparse

os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(_BASE_DIR, 'src'))

import numpy as np

from model_loader import load_inference_model
from segmentation import (
    Segmenter, CURRENT_CONFIG, P1_CONFIG,
    extract_keypoints_48, is_active_hand, resample_gesture_linspace,
    MAX_FRAMES,
)


def _load_classes():
    with open(os.path.join(_BASE_DIR, 'models', 'classes.json'), 'r', encoding='utf-8') as f:
        return json.load(f)


def _collect_videos(class_names, n_videos, seed=7):
    """Lấy mẫu video GỐC thuộc TEST-SPLIT (model chưa từng gặp lúc train).

    Trước đây chọn từ toàn bộ dataset (train+test) -> số liệu bị thổi phồng do
    memorization, đúng cái lỗi mà bản cũ mắc phải. Ở đây map mỗi file .npy trong
    `data/keypoints_splited/test` (tên `vsl400_<id>` / `online_<id>`, thư mục cha
    = gloss) về đúng file mp4 gốc tương ứng, và chỉ giữ những id nằm trong test.
    """
    test_dir = os.path.join(_BASE_DIR, 'data', 'keypoints_splited', 'test')
    if not os.path.isdir(test_dir):
        return []

    # id -> path cho toàn bộ mp4 VSL400.
    vsl_root = os.path.join(_BASE_DIR, 'Dataset', 'raw', 'raw', 'VSL400')
    id_to_path = {}
    for part in sorted(os.listdir(vsl_root)):
        pj = os.path.join(vsl_root, part)
        if not os.path.isdir(pj):
            continue
        for split in sorted(os.listdir(pj)):
            vd = os.path.join(pj, split, 'front_view')
            if not os.path.isdir(vd):
                continue
            for f in os.listdir(vd):
                if f.endswith('.mp4'):
                    id_to_path.setdefault(f[:-4], os.path.join(vd, f))
    online_test_dir = os.path.join(_BASE_DIR, 'Dataset', 'raw', 'raw', 'online_sourced', 'test')

    class_set = set(class_names)
    per_class = {}
    for gloss in sorted(os.listdir(test_dir)):
        gdir = os.path.join(test_dir, gloss)
        if not os.path.isdir(gdir) or gloss not in class_set:
            continue
        for f in sorted(os.listdir(gdir)):
            if not f.endswith('.npy'):
                continue
            stem = f[:-4]
            if stem.startswith('vsl400_'):
                vid = stem[len('vsl400_'):]
                path = id_to_path.get(vid)
            elif stem.startswith('online_'):
                vid = stem[len('online_'):]
                path = os.path.join(online_test_dir, vid + '.mp4')
                path = path if os.path.exists(path) else None
            else:
                path = None
            if path:
                per_class.setdefault(gloss, []).append((path, gloss))
                break  # 1 video test / class để đủ phủ từ vựng

    pool = [cands[0] for cands in per_class.values() if cands]
    random.Random(seed).shuffle(pool)
    return pool[:n_videos]


def _extract_frames(video_path, holistic, flip=False, cfg=CURRENT_CONFIG):
    """Trả về list (keypoints(48,3), hands_present) cho mỗi frame, mô phỏng webcam."""
    import cv2
    cap = cv2.VideoCapture(video_path)
    frames = []
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if flip:
                frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb.flags.writeable = False
            results = holistic.process(rgb)
            kp = extract_keypoints_48(results)
            hp = is_active_hand(results.left_hand_landmarks, results.pose_landmarks) or \
                is_active_hand(results.right_hand_landmarks, results.pose_landmarks)
            frames.append((kp, hp))
    finally:
        cap.release()
    return frames


def _inject_hold(frames, hold_frames):
    """Giả lập user giữ tay im trong khung SAU khi ký xong (motion->0, hands_present=True).

    Đây là trạng thái xảy ra liên tục trên webcam nhưng KHÔNG có trong video studio
    (hết clip người mẫu hạ tay), nên benchmark cũ không bao giờ bắt được lỗi bloat.
    Chèn vào TRƯỚC khi Segmenter chạy -> test đúng năng lực KẾT THÚC ký hiệu.
    """
    if not frames or hold_frames <= 0:
        return list(frames)
    last_kp = frames[-1][0]
    return list(frames) + [(last_kp.copy(), True) for _ in range(hold_frames)]


def _run_segmenter(frames, cfg, hold_frames=0):
    """Chạy Segmenter production trên luồng frame (+ bloat nếu có), trả list cử chỉ.

    Flush cử chỉ đang dở khi HẾT LUỒNG: video studio giữ tay tới khung cuối nên
    `hands_missing` không kích hoạt; không flush thì kịch bản "clean" không chốt được
    từ nào (đây chính là lỗi im-lặng của TASK-013 trên dữ liệu này).
    """
    stream = _inject_hold(frames, hold_frames) if hold_frames else frames
    seg = Segmenter(cfg)
    out = []
    for kp, hp in stream:
        res = seg.feed(kp, hp)
        if res:
            out.append(res[0])
    pending = seg.pending_gesture
    if pending is not None and len(pending) >= cfg.min_gesture_frames:
        out.append(tuple(pending))
    return out


def _acc(correct, total):
    return (correct / total * 100.0) if total else 0.0


def run_benchmark(n_videos=40, samples_per_class=1, hold_frames=40, verbose=True):
    import cv2
    import mediapipe as mp

    class_names = _load_classes()
    num_classes = len(class_names)

    print('=' * 78)
    print('📊 BENCHMARK E2E PHÂN ĐOẠN CỬ CHỈ (đọc VIDEO GỐC + chạy đúng Segmenter)')
    print('=' * 78)
    print(f'  • Từ điển: models/classes.json  ({num_classes} lớp)')
    print(f'  • Số video gốc VSL400: {n_videos}')
    print(f'  • Frame "giữ tay im" giả lập bloat: {hold_frames}')

    model, path = load_inference_model(os.path.join(_BASE_DIR, 'models'),
                                       (MAX_FRAMES, 48, 3), num_classes)
    print(f'  • Checkpoint: {os.path.basename(path)}')

    videos = _collect_videos(class_names, n_videos)
    if verbose:
        print(f'  • Đã tìm {len(videos)} video khả dụng\n')

    mp_holistic = mp.solutions.holistic

    # ---------------- A. Trần trên: whole clip -> linspace 60 (không phân đoạn) -------
    # Dùng dữ liệu .npy chuẩn train làm tham chiếu nhanh độ nhạy của model với phân phối train.
    ref_correct = ref_total = 0
    test_dir = os.path.join(_BASE_DIR, 'data', 'keypoints_splited', 'test')
    if os.path.isdir(test_dir):
        random.Random(0).shuffle(videos)  # just to vary seeds downstream
        dirs = sorted([d for d in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, d))])
        rs = random.Random(0)
        npy_samples = []
        for d in dirs:
            cdir = os.path.join(test_dir, d)
            fs = [f for f in os.listdir(cdir) if f.endswith('.npy')]
            rs.shuffle(fs)
            for f in fs[:samples_per_class]:
                npy_samples.append((d, np.load(os.path.join(cdir, f)).astype(np.float32)))
        rs.shuffle(npy_samples)
        npy_samples = npy_samples[:300]
        X = np.stack([resample_gesture_linspace(a, MAX_FRAMES) for _, a in npy_samples]) \
            .reshape(len(npy_samples), MAX_FRAMES, 144).astype(np.float32)
        preds = np.concatenate([model.predict(X[i:i + 128], verbose=0) for i in range(0, len(X), 128)])
        order = np.argsort(preds, axis=1)[:, ::-1]
        ref_correct = sum(1 for k, (lab, _) in enumerate(npy_samples) if class_names[order[k, 0]] == lab)
        ref_total = len(npy_samples)
        if verbose:
            print(f'--- intrinsic-npy (độ chính xác VỐN CÓ của model, KHÔNG phải pipeline) ---')
            print(f'  {ref_correct}/{ref_total} = {_acc(ref_correct, ref_total):.2f}%  '
                  f'(mẫu chuẩn train, đã resample sẵn 60f)\n')

    # ---------------- E2E qua VIDEO GỐC + Segmenter production ----------------
    scenarios = [
        ('B1 current/clean', CURRENT_CONFIG, 0, False),
        ('B2 current/BLOAT', CURRENT_CONFIG, hold_frames, False),
        ('C1 P1/clean', P1_CONFIG, 0, False),
        ('C2 P1/BLOAT', P1_CONFIG, hold_frames, False),
        ('D  current/FLIP', CURRENT_CONFIG, 0, True),
    ]

    # Tiền trích xuất landmark MỖI video MỘT lần (clean + flip) để tiết kiệm MediaPipe.
    frames_clean, frames_flip, glosses = [], [], []
    holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    try:
        for vp, g in videos:
            if g not in class_names:
                continue
            fc = _extract_frames(vp, holistic, flip=False)
            if len(fc) < 15:
                continue
            frames_clean.append(fc)
            glosses.append(g)
            frames_flip.append(_extract_frames(vp, holistic, flip=True))
    finally:
        holistic.close()

    if not frames_clean:
        print('❌ Không trích được video nào.')
        return False

    n = len(glosses)
    results = {}
    for label, cfg, hold, use_flip in scenarios:
        srcs = frames_flip if use_flip else frames_clean
        seq_lists = []
        for fc in srcs:
            segs = _run_segmenter(fc, cfg, hold)
            segs = [s for s in segs if len(s) >= cfg.min_gesture_frames]
            if not segs:
                seq_lists.append(None)
                continue
            longest = max(segs, key=len)
            seq_lists.append(resample_gesture_linspace(list(longest), MAX_FRAMES))
        valid = [(i, s) for i, s in enumerate(seq_lists) if s is not None]
        if not valid:
            results[label] = (0, 0)
            if verbose:
                print(f'  {label:18s} : 0 video segment được')
            continue
        X = np.stack([s for _, s in valid]).reshape(len(valid), MAX_FRAMES, 144).astype(np.float32)
        preds = np.concatenate([model.predict(X[i:i + 64], verbose=0) for i in range(0, len(X), 64)])
        order = np.argsort(preds, axis=1)[:, ::-1]
        ok = sum(1 for k, (idx, _) in enumerate(valid) if class_names[order[k, 0]] == glosses[idx])
        results[label] = (ok, len(valid))
        if verbose:
            print(f'  {label:18s} : {ok}/{len(valid)} = {_acc(ok, len(valid)):5.1f}%')

    print('-' * 78)
    # Trần trên: whole clip -> linspace (upper bound e2e thực sự)
    whole_seqs, whole_gloss = [], []
    for fc, g in zip(frames_clean, glosses):
        whole_seqs.append(resample_gesture_linspace([f[0] for f in fc], MAX_FRAMES))
        whole_gloss.append(g)
    Xw = np.stack(whole_seqs).reshape(len(whole_seqs), MAX_FRAMES, 144).astype(np.float32)
    pw = np.concatenate([model.predict(Xw[i:i + 64], verbose=0) for i in range(0, len(Xw), 64)])
    ow = np.argsort(pw, axis=1)[:, ::-1]
    wok = sum(1 for k, gg in enumerate(whole_gloss) if class_names[ow[k, 0]] == gg)
    print(f'  {"A whole-clip":18s} : {wok}/{n} = {_acc(wok, n):5.1f}%  (TRẦN, không phân đoạn)')

    print('\n  DIỄN GIẢI  ' + '=' * 64)
    notes = {
        'B1 current/clean': 'TASK-013, user hạ tay đúng cách',
        'B2 current/BLOAT': '← LỖI SỐNG CÒN: user giữ tay im',
        'C1 P1/clean': 'P1, hành vi chuẩn',
        'C2 P1/BLOAT': '→ P1 đã vá bloat (stillness detector)',
        'D  current/FLIP': 'đo độ nhạy mirror tay',
    }
    for label, (ok, tot) in results.items():
        print(f'    {label:18s} = {_acc(ok, tot) if tot else 0:5.1f}%  {notes.get(label, "")}')
    print('=' * 78)

    # Nghiệm thu: cả hai máy phải ≥85% khi clean, VÀ P1 không được tệ hơn current
    # khi bloat; lý tưởng P1 > current vì stillness detector cắt bớt frame giữ-yên.
    acc_b1 = _acc(*results['B1 current/clean']) if results['B1 current/clean'][1] else 0.0
    acc_c1 = _acc(*results['C1 P1/clean']) if results['C1 P1/clean'][1] else 0.0
    acc_b2 = _acc(*results['B2 current/BLOAT']) if results['B2 current/BLOAT'][1] else 0.0
    acc_c2 = _acc(*results['C2 P1/BLOAT']) if results['C2 P1/BLOAT'][1] else 0.0
    passed = (acc_c1 >= 85.0 and acc_c2 >= 85.0 and acc_c2 >= acc_b2)
    print(f'\n🏁 PASS criteria: P1/clean {acc_c1:.1f}% ≥85%  VÀ  P1/bloat {acc_c2:.1f}% ≥85%  VÀ  '
          f'P1/bloat {acc_c2:.1f}% ≥ current/bloat {acc_b2:.1f}% → '
          f'{"✅ PASS" if passed else "❌ FAIL"}')
    print(f'   current: clean {acc_b1:.1f}% → bloat {acc_b2:.1f}% (mất {acc_b1-acc_b2:.1f}pp khi giữ tay)')
    print(f'   P1     : clean {acc_c1:.1f}% → bloat {acc_c2:.1f}% (mất {acc_c1-acc_c2:.1f}pp khi giữ tay)')
    return passed


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--videos', type=int, default=40)
    p.add_argument('--samples', type=int, default=1)
    p.add_argument('--hold', type=int, default=40, help='Số frame GIỮ TAY IM giả lập bloat')
    a = p.parse_args()
    ok = run_benchmark(a.videos, a.samples, a.hold)
    sys.exit(0 if ok else 1)
