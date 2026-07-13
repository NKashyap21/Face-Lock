import os
import glob
from helpers import (
    REFERENCE_DIR,
    FRAMES_PER_ATTEMPT,
    clear_dir,
    capture_frames,
    get_averaged_embedding,
)


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

    print(f"Capturing {FRAMES_PER_ATTEMPT} enrollment frames...")
    frames = capture_frames(FRAMES_PER_ATTEMPT, REFERENCE_DIR)

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
    enroll()