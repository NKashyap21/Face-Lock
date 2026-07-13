from torch.nn.functional import cosine_similarity
from helpers import (
    DEVICE,
    THRESHOLD,
    AMBIGUOUS_MARGIN,
    MAX_RESCANS,
    FRAMES_PER_ATTEMPT,
    MIN_VALID_DETECTIONS,
    clear_dir,
    capture_frames,
    get_averaged_embedding,
    load_reference_embedding,
    check_liveness
)


def authenticate():
    ref_centroid = load_reference_embedding()

    attempt = 0
    while attempt <= MAX_RESCANS:
        label = "Initial scan" if attempt == 0 else f"Rescan {attempt}"
        print(f"{label}: capturing {FRAMES_PER_ATTEMPT} frames...")

        frames = capture_frames(FRAMES_PER_ATTEMPT)
        
        if not check_liveness(frames):
            print("Liveness check failed — no blink detected. Possible spoofing attempt.")
            attempt += 1
            continue

        inf_emb = get_averaged_embedding(frames, min_valid=MIN_VALID_DETECTIONS)

        if inf_emb is None:
            print("No reliable face detected this attempt.")
            attempt += 1
            continue

        sim = cosine_similarity(inf_emb, ref_centroid, dim=-1).item()
        print(f"Similarity: {sim:.4f}")

        is_last_attempt = attempt == MAX_RESCANS

        if sim > THRESHOLD + AMBIGUOUS_MARGIN:
            print("Allow")
        
            return True

        elif sim < THRESHOLD - AMBIGUOUS_MARGIN or is_last_attempt:
            print("Rejected")
            return False

        else:
            print("Ambiguous result — rescanning...")
            attempt += 1

    print("Rejected (max rescans reached)")
    return False


if __name__ == "__main__":
    print(f"Running on {DEVICE}")
    result = authenticate()
    print("AUTHENTICATED" if result else "ACCESS DENIED")