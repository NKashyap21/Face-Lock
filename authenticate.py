from torch.nn.functional import cosine_similarity
from helpers import (
    DEVICE,
    INFERENCE_DIR,
    THRESHOLD,
    AMBIGUOUS_MARGIN,
    MAX_RESCANS,
    FRAMES_PER_ATTEMPT,
    MIN_VALID_DETECTIONS,
    clear_dir,
    capture_frames,
    get_averaged_embedding,
    load_reference_centroid,
    # promote_inference_to_reference,  # uncomment when ready to enable
)


def authenticate():
    ref_centroid = load_reference_centroid()

    attempt = 0
    while attempt <= MAX_RESCANS:
        clear_dir(INFERENCE_DIR)
        label = "Initial scan" if attempt == 0 else f"Rescan {attempt}"
        print(f"{label}: capturing {FRAMES_PER_ATTEMPT} frames...")

        frames = capture_frames(FRAMES_PER_ATTEMPT, INFERENCE_DIR)
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
            # promote_inference_to_reference()  # enable when ready
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