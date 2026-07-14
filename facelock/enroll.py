from facelock.config import (
    REFERENCE_DIR,
    FRAMES_PER_ATTEMPT,
)
from facelock.camera import capture_frames
from facelock.embeddings import get_averaged_embedding
from facelock.liveness import check_liveness
import torch
import os
import glob
import logging 

logger = logging.getLogger(__name__)

def clear_dir(path):
    os.makedirs(path, exist_ok=True)
    for f in glob.glob(os.path.join(path, "*")):
        os.remove(f)

def enroll():
    ref_emb = glob.glob(os.path.join(REFERENCE_DIR,"*.pt"))
    mode = "replace"
    if ref_emb:
        choice = input(
            f"A reference embedding was found."
            f"(R)eplace, (C)ancel?  " 
        ).strip().lower()
        if choice == "c":
            print("Enrollment Cancelled.")
            return False
        elif choice == "r":
            mode = "replace"
        else:
            print("Invalid.")
            return False
    
    logger.info(f"Capturing {FRAMES_PER_ATTEMPT} enrollment frames... please blink naturally.")
    frames = capture_frames(FRAMES_PER_ATTEMPT)
    if not check_liveness(frames):
        logger.critical("Enrollment failed — no blink detected. Please try again with a live face.")
        return False
    
    logger.debug("Getting average embeddings...")
    valid_emb = get_averaged_embedding(frames, min_valid=1)
    if valid_emb is None:
        logger.critical("Enrollment failed — no face detected in any captured frame.")
        return False
    if mode == "replace":
        clear_dir(REFERENCE_DIR)
    
    torch.save(valid_emb,f"{REFERENCE_DIR}/referance.pt")
    logger.info("Enrollment Successfull")
    return True 


if __name__ == "__main__":
    enroll()
