import cv2
from PIL import Image
import time 
import logging

logger = logging.getLogger(__name__)

def capture_frames(num_frames):
    """Capture frames from webcam, save to save_dir, return list of PIL Images."""
    logger.info("Opening webcam...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.critical("Could not open webcam")        
        raise RuntimeError("Could not open webcam")

    frames = []
    count = 0
    logger.info("Generating Frames...")
    while count < num_frames:
        ret, frame = cap.read()
        if not ret:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        frames.append(img)

        count += 1
        time.sleep(0.1)
    logger.info(f"Generated {num_frames} frames.")

    cap.release()
    return frames