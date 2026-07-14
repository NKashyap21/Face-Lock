import numpy as np 
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from facelock.config import FACE_LANDMARKER_MODEL_PATH,EAR_THRESHOLD


# 6-point eye landmark indices from mediapipe's 468-point Face Mesh
# Order matches dlib's EAR convention: [left_corner, top1, top2, right_corner, bottom1, bottom2]
LEFT_EYE_IDX = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_IDX = [33, 160, 158, 133, 153, 144]

_base_options = mp_python.BaseOptions(model_asset_path=FACE_LANDMARKER_MODEL_PATH)
_landmarker_options = mp_vision.FaceLandmarkerOptions(
    base_options=_base_options,
    running_mode=mp_vision.RunningMode.IMAGE,
    num_faces=1,
)
_face_landmarker = mp_vision.FaceLandmarker.create_from_options(_landmarker_options)


def _distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))


def _eye_aspect_ratio(landmarks, eye_idx, img_w, img_h):
    points = [(landmarks[i].x * img_w, landmarks[i].y * img_h) for i in eye_idx]
    p1, p2, p3, p4, p5, p6 = points
    vertical1 = _distance(p2, p6)
    vertical2 = _distance(p3, p5)
    horizontal = _distance(p1, p4)
    if horizontal == 0:
        return None
    return (vertical1 + vertical2) / (2.0 * horizontal)


def check_liveness(images):
    """
    Runs mediapipe FaceLandmarker across a sequence of PIL images and checks
    for a genuine blink pattern (EAR dips below threshold, then recovers).
    Returns True if a blink was detected, False otherwise.
    """
    ear_values = []

    for img in images:
        img_np = np.array(img.convert("RGB"))
        h, w, _ = img_np.shape
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_np)

        result = _face_landmarker.detect(mp_image)

        if not result.face_landmarks:
            continue

        landmarks = result.face_landmarks[0]  # first (only) detected face
        left_ear = _eye_aspect_ratio(landmarks, LEFT_EYE_IDX, w, h)
        right_ear = _eye_aspect_ratio(landmarks, RIGHT_EYE_IDX, w, h)

        if left_ear is None or right_ear is None:
            continue

        ear_values.append((left_ear + right_ear) / 2.0)

    if len(ear_values) < 3:
        print(f"Liveness check: only {len(ear_values)} usable frames — insufficient")
        return False

    print(f"EAR sequence: {[round(e, 3) for e in ear_values]}")

    was_open = any(e > EAR_THRESHOLD for e in ear_values)
    was_closed = any(e <= EAR_THRESHOLD for e in ear_values)

    blinked = was_open and was_closed
    print(f"Blink detected: {blinked}")
    return blinked