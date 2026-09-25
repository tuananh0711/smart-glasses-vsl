"""
segmentation.py — Modular dùng chung cho Machine trạng thái 4 pha + tiền xử lý landmark.

Mục đích sinh ra từ TASK-013 review (qc_report.md, Kỳ 2):
    Benchmark cũ mô phỏng state machine trên dữ liệu `.npy` ĐÃ resample 60 frame,
    nên "State Machine MỚI" ≡ "chuẩn train" (đồng nhất thức) và không phát hiện
    được regression trên luồng live. File này chứa ĐÚNG một bản cài đặt state
    machine để cả `inference_webcam.py`, `inference_pi_tflite.py` và
    `eval_segmentation.py` cùng chạy — loại bỏ tình trạng copy-paste 3 nơi.

Ranh giới ADR: không import TFLite/MediaPipe/TensorFlow ở đây; module thuần numpy
để chạy được cả trên Raspberry Pi headless lẫn trong benchmark trên PC.
"""

from dataclasses import dataclass, replace
from typing import List, Optional

import numpy as np

NUM_POINTS = 48
NUM_DIMS = 3
MAX_FRAMES = 60
POSE_INDICES = (11, 12, 13, 14, 15, 16)


def extract_keypoints_48(results) -> np.ndarray:
    """Trích 48 điểm 3D + chuẩn hóa tịnh tiến/co giãn theo 2 vai.

    Giống 100% `preprocess.extract_keypoints_48` (nguồn dữ liệu huấn luyện):
      - 6 pose (vai/khuỷu/cổ tay) + 21 tay trái + 21 tay phải.
      - gốc tọa độ = trung điểm 2 vai, scale = khoảng cách 2 vai.
      - điểm có visibility <= 0.5 hoặc không tìm thấy -> vector 0.
    """
    pose = np.zeros((6, 3), dtype=np.float32)
    center_x, center_y, center_z, scale = 0.5, 0.5, 0.0, 1.0

    if results.pose_landmarks:
        for i, idx in enumerate(POSE_INDICES):
            lm = results.pose_landmarks.landmark[idx]
            if hasattr(lm, 'visibility') and lm.visibility > 0.5:
                pose[i] = [lm.x, lm.y, lm.z]
            elif not hasattr(lm, 'visibility'):
                pose[i] = [lm.x, lm.y, lm.z]
            else:
                pose[i] = [0.0, 0.0, 0.0]

        if not np.array_equal(pose[0], [0.0, 0.0, 0.0]) and not np.array_equal(pose[1], [0.0, 0.0, 0.0]):
            center_x = (pose[0][0] + pose[1][0]) / 2
            center_y = (pose[0][1] + pose[1][1]) / 2
            center_z = (pose[0][2] + pose[1][2]) / 2
            dist = np.linalg.norm(pose[0] - pose[1])
            if dist > 0.01:
                scale = dist

    lh = np.zeros((21, 3), dtype=np.float32)
    if results.left_hand_landmarks:
        for i, lm in enumerate(results.left_hand_landmarks.landmark):
            lh[i] = [lm.x, lm.y, lm.z]

    rh = np.zeros((21, 3), dtype=np.float32)
    if results.right_hand_landmarks:
        for i, lm in enumerate(results.right_hand_landmarks.landmark):
            rh[i] = [lm.x, lm.y, lm.z]

    keypoints = np.concatenate([pose, lh, rh]).astype(np.float32)

    for i in range(keypoints.shape[0]):
        if not np.array_equal(keypoints[i], [0.0, 0.0, 0.0]):
            keypoints[i][0] = (keypoints[i][0] - center_x) / scale
            keypoints[i][1] = (keypoints[i][1] - center_y) / scale
            keypoints[i][2] = (keypoints[i][2] - center_z) / scale

    return keypoints


def hand_motion(prev_kp: Optional[np.ndarray], curr_kp: Optional[np.ndarray]) -> float:
    """Vận tốc trung vị (median) của cổ tay + 42 điểm bàn tay giữa 2 frame liên tiếp."""
    if prev_kp is None or curr_kp is None:
        return 0.0
    prev_pts, curr_pts = [], []
    for idx in range(4, NUM_POINTS):
        p_prev, p_curr = prev_kp[idx], curr_kp[idx]
        if not np.array_equal(p_prev, [0.0, 0.0, 0.0]) and not np.array_equal(p_curr, [0.0, 0.0, 0.0]):
            prev_pts.append(p_prev)
            curr_pts.append(p_curr)
    if not prev_pts:
        return 0.0
    diffs = np.linalg.norm(np.array(curr_pts) - np.array(prev_pts), axis=1)
    return float(np.median(diffs))


def resample_gesture_linspace(gesture_list, target_frames: int = MAX_FRAMES) -> np.ndarray:
    """Đưa chuỗi T frame về đúng 60 frame theo đúng quy tắc `preprocess.py`.

    - T >= 60: nội suy chỉ số `np.linspace(0, T - 1, 60)`.
    - T <  60: giữ nguyên T frame và zero-pad ở ĐUÔI (khớp các mẫu clip ngắn trong train).
    """
    T = len(gesture_list)
    if T == 0:
        return np.zeros((target_frames, NUM_POINTS, NUM_DIMS), dtype=np.float32)
    if T >= target_frames:
        indices = np.linspace(0, T - 1, target_frames, dtype=int)
        return np.array([gesture_list[i] for i in indices], dtype=np.float32)
    resampled = list(gesture_list)
    zero_frame = np.zeros((NUM_POINTS, NUM_DIMS), dtype=np.float32)
    while len(resampled) < target_frames:
        resampled.append(zero_frame)
    return np.array(resampled, dtype=np.float32)


@dataclass(frozen=True)
class SegmenterConfig:
    """Toàn bộ hằng số phân đoạn, để benchmark đổi tham số mà không sửa production."""

    pre_roll_frames: int = 4
    start_confirm_frames: int = 3
    hands_missing_frames: int = 10
    min_gesture_frames: int = 12
    max_gesture_frames: int = 100
    start_motion_threshold: float = 0.020
    # stillness end-detector (P1). end_still_frames = 0 nghĩa là TẮT (hành vi TASK-013).
    end_motion_threshold: float = 0.022
    end_still_frames: int = 0
    keep_tail_frames: int = 3
    cooldown_frames: int = 8
    motion_alpha: float = 0.3
    wrist_rest_y: float = 0.95
    wrist_fallback_y: float = 0.92
    shoulder_span_min: float = 0.02
    wrist_below_shoulder_span: float = 2.5


# Hành vi đúng như TASK-013 đã deploy (không có end-detector). Dùng làm nhánh "trước".
CURRENT_CONFIG = SegmenterConfig()

# P1: bật lại stillness end-detector với ngưỡng đã hiệu chỉnh theo phân phối dữ liệu
# (chuỗi đứng-yên giữa ký rất ngắn: p99 = 8 frame trên npy resampled; native-video
# sweep: max 10 frame @0.022 -> 14 an toàn; xem qc_report.md Kỳ 3). pre_roll dày hơn
# để không cắt mất handshape mở đầu, và ARMING abort không xóa pre_roll nữa.
P1_CONFIG = SegmenterConfig(
    pre_roll_frames=12,
    start_confirm_frames=2,
    hands_missing_frames=8,
    end_still_frames=14,
    end_motion_threshold=0.022,
)


def is_active_hand(hand_landmarks, pose_landmarks=None, cfg: SegmenterConfig = CURRENT_CONFIG) -> bool:
    """Tay đang ở trong vùng ký hiệu hay đã hạ xuống nghỉ."""
    if hand_landmarks is None:
        return False
    wrist_y = hand_landmarks.landmark[0].y
    if pose_landmarks is not None and len(pose_landmarks.landmark) > 12:
        sh_y = (pose_landmarks.landmark[11].y + pose_landmarks.landmark[12].y) / 2
        sh_dist = abs(pose_landmarks.landmark[11].x - pose_landmarks.landmark[12].x)
        if sh_dist > cfg.shoulder_span_min:
            return wrist_y < (sh_y + cfg.wrist_below_shoulder_span * sh_dist) and wrist_y < cfg.wrist_rest_y
    return wrist_y < cfg.wrist_fallback_y


class Segmenter:
    """Máy trạng thái 4 pha: IDLE -> ARMING -> RECORDING -> FINALIZING -> cooldown.

    `feed()` nhận kết quả của MỘT frame và trả về `None`, hoặc một tuple
    `(gesture_frames, reason)` khi một cử chỉ hoàn chỉnh sẵn sàng để suy luận.
    Người gọi chịu trách nhiệm resample + inference.
    """

    def __init__(self, cfg: SegmenterConfig = P1_CONFIG):
        self.cfg = cfg
        self.reset(hard=True)

    @property
    def state(self) -> str:
        return self._state

    @property
    def record_len(self) -> int:
        """Số frame hiện đang thu trong trạng thái RECORDING (0 nếu không thu)."""
        return len(self._gesture) if self._state == "RECORDING" else 0

    @property
    def pending_gesture(self) -> Optional[tuple]:
        """Cử chỉ đang dở trong RECORDING (để flush khi dừng luồng/chương trình)."""
        if self._state == "RECORDING" and len(self._gesture) >= self.cfg.min_gesture_frames:
            return tuple(self._gesture)
        return None

    def reset(self, hard: bool = True):
        cfg = self.cfg
        self._state = "IDLE"
        self._pre_roll: List[np.ndarray] = []
        self._gesture: List[np.ndarray] = []
        self._arming = 0
        self._still = 0
        self._missing = 0
        self._cooldown = 0
        self._smoothed = 0.0
        self._prev_kp: Optional[np.ndarray] = None
        if hard:
            self.frames_seen = 0

    def feed(self, keypoints: np.ndarray, hands_present: bool) -> Optional[tuple]:
        """Đưa một frame đã trích xuất vào máy trạng thái.

        Args:
            keypoints: mảng (48, 3) đã chuẩn hóa của frame hiện tại.
            hands_present: `is_active_hand()` trả về True cho trái HOẶC phải.
        Returns:
            `None` nếu chưa chốt từ, hoặc `(tuple(frames), reason_str)`.
        """
        cfg = self.cfg
        if self._cooldown > 0:
            self._cooldown -= 1
            self._state = "IDLE"
            self._pre_roll = []
            self._arming = 0
            self._smoothed = 0.0
            self._prev_kp = None
            return None

        raw = hand_motion(self._prev_kp, keypoints)
        self._smoothed = (1 - cfg.motion_alpha) * self._smoothed + cfg.motion_alpha * raw
        self._prev_kp = keypoints

        if self._state == "IDLE":
            self._pre_roll = (self._pre_roll + [keypoints])[-cfg.pre_roll_frames:]
            if len(self._pre_roll) == cfg.pre_roll_frames and hands_present and self._smoothed > cfg.start_motion_threshold:
                self._state = "ARMING"
                self._arming = 1
            return None

        if self._state == "ARMING":
            self._pre_roll = (self._pre_roll + [keypoints])[-cfg.pre_roll_frames:]
            if hands_present and self._smoothed > cfg.start_motion_threshold:
                self._arming += 1
                if self._arming >= cfg.start_confirm_frames:
                    self._state = "RECORDING"
                    self._gesture = list(self._pre_roll)
                    self._arming = 0
                    self._still = 0
                    self._missing = 0
            else:
                # P1 fix: quay về IDLE nhưng GIỮ pre_roll đã tích lũy, không xóa sạch.
                # Bản TASK-013 xóa buffer -> phải mất lại `pre_roll_frames` frame để
                # khởi động lại, nên phần đầu của ký hiệu (handshape mở đầu) hay bị cắt.
                self._state = "IDLE"
                self._arming = 0
            return None

        if self._state == "RECORDING":
            self._gesture.append(keypoints)
            self._missing = self._missing + 1 if not hands_present else 0
            self._still = self._still + 1 if self._smoothed < cfg.end_motion_threshold else 0

            reason = None
            if self._missing >= cfg.hands_missing_frames:
                reason = "hands_missing"
                self._drop_tail(self._missing)
            elif cfg.end_still_frames and self._still >= cfg.end_still_frames and len(self._gesture) >= cfg.min_gesture_frames:
                reason = "still"
                # Chỉ bỏ phần đứng yên thừa, giữ lại `keep_tail_frames` để khớp đuôi
                # clip huấn luyện (train giữ nguyên frame nghỉ ở cuối).
                self._drop_tail(max(0, self._still - cfg.keep_tail_frames))
            elif len(self._gesture) >= cfg.max_gesture_frames:
                reason = "max_frames"

            if reason:
                if len(self._gesture) < cfg.min_gesture_frames:
                    self.reset(hard=False)
                    self._cooldown = cfg.cooldown_frames
                    return None
                frames = tuple(self._gesture)
                self.reset(hard=False)
                self._cooldown = cfg.cooldown_frames
                return frames, reason
            return None

        return None

    def _drop_tail(self, n: int):
        n = min(n, max(0, len(self._gesture) - 1))
        if n > 0:
            self._gesture = self._gesture[:-n]

    def model_input(self, frames) -> np.ndarray:
        """Resample một cử chỉ đã chốt sang đúng shape model (60, 144)."""
        seq = resample_gesture_linspace(list(frames), MAX_FRAMES)
        return np.expand_dims(seq, axis=0).reshape(1, MAX_FRAMES, NUM_POINTS * NUM_DIMS).astype(np.float32)
