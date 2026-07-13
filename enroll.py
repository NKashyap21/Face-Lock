import torch
import os
import glob
from helpers import (
    REFERENCE_DIR,
    FRAMES_PER_ATTEMPT,
    clear_dir,
    capture_frames,
    get_averaged_embedding,
    check_liveness,
)

def my_enrol():
    ref_emb = glob.glob(os.path.join(REFERENCE_DIR,"*.pt"))
    mode = "replace"
    if ref_emb:
        choice = input(
            f"A reference embedding was found."
            f"(R)eplace, (C)ancel"
        ).strip().lower()
        if choice == "c":
            print("Enrollment Cancelled.")
            return False
        elif choice == "r":
            mode = "replace"
        else:
            print("Invalid.")
            return False
    
    print(f"Capturing {FRAMES_PER_ATTEMPT} enrollment frames... please blink naturally.")
    frames = capture_frames(FRAMES_PER_ATTEMPT,REFERENCE_DIR)
    if not check_liveness(frames):
        print("Enrollment failed — no blink detected. Please try again with a live face.")
        return False
    
    valid_emb = get_averaged_embedding(frames, min_valid=1)
    if valid_emb is None:
        print("Enrollment failed — no face detected in any captured frame.")
        return False
    if mode == "replace":
        clear_dir(REFERENCE_DIR)
    
    torch.save(valid_emb,f"{REFERENCE_DIR}/referance.pt")
    print("Enrollment Successfull")
    return True 

def enroll():
    ref_files = glob.glob(os.path.join(REFERENCE_DIR, "*"))
    mode = "replace"

    if ref_files:
        choice = input(
            f"{len(ref_files)} reference images already exist. "
            f"(R)eplace, (A)dd, (C)ancel? "
        ).strip().lower()

        if choice == "c":
            print("Enrollment cancelled.")
            return False
        elif choice == "a":
            mode = "add"
        elif choice == "r":
            mode = "replace"
        else:
            print("Invalid choice, cancelling.")
            return False

    if mode == "replace":
        clear_dir(REFERENCE_DIR)

    print(f"Capturing {FRAMES_PER_ATTEMPT} enrollment frames... please blink naturally.")
    frames = capture_frames(FRAMES_PER_ATTEMPT, REFERENCE_DIR)

    if not check_liveness(frames):
        print("Enrollment failed — no blink detected. Please try again with a live face.")
        for f in glob.glob(os.path.join(REFERENCE_DIR, "capture_*")):
            os.remove(f)
        return False

    valid_emb = get_averaged_embedding(frames, min_valid=1)
    if valid_emb is None:
        print("Enrollment failed — no face detected in any captured frame.")
        for f in glob.glob(os.path.join(REFERENCE_DIR, "capture_*")):
            os.remove(f)
        return False

    total = len(glob.glob(os.path.join(REFERENCE_DIR, "*")))
    print(f"Enrollment successful. {total} reference image(s) now stored in {REFERENCE_DIR}.")
    return True


if __name__ == "__main__":
    my_enrol()
