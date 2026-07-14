import cv2
from PIL import Image
import time 

def capture_frames(num_frames):
    """Capture frames from webcam, save to save_dir, return list of PIL Images."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")

    frames = []
    count = 0
    while count < num_frames:
        ret, frame = cap.read()
        if not ret:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        frames.append(img)

        count += 1
        time.sleep(0.2)

    cap.release()
    return frames