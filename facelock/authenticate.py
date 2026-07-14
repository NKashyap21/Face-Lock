from torch.nn.functional import cosine_similarity
from facelock.config import (
    DEVICE,
    THRESHOLD,
    AMBIGUOUS_MARGIN,
    MAX_RESCANS,
    FRAMES_PER_ATTEMPT,
    MIN_VALID_DETECTIONS
)
from facelock.camera import capture_frames
from facelock.embeddings import get_averaged_embedding,load_reference_embedding
from facelock.liveness import check_liveness
from facelock.benchmark import BenchmarkTimer
import logging
logger = logging.getLogger(__name__)


def authenticate():
    with BenchmarkTimer("Total authentication time", logger):
        with BenchmarkTimer("Loading reference embedding", logger):
            ref_centroid = load_reference_embedding()

        attempt = 0
        while attempt <= MAX_RESCANS:
            label = "Initial scan" if attempt == 0 else f"Rescan {attempt}"

            logger.info("Capturing Frames...")
            with BenchmarkTimer("Camera frame capture", logger):
                frames = capture_frames(FRAMES_PER_ATTEMPT)
            
            with BenchmarkTimer("Liveness detection", logger):
                is_live = check_liveness(frames)
            if not is_live:
                logger.warning("Liveness check failed. No blink detected. Possible spoofing attempt")
                attempt += 1
                continue
            logger.info("Getting average embedding...")
            with BenchmarkTimer("Embedding generation", logger):
                inf_emb = get_averaged_embedding(frames, min_valid=MIN_VALID_DETECTIONS)

            if inf_emb is None:
                logger.warning("No reliable face detected this attempt.")
                attempt += 1
                continue

            with BenchmarkTimer("Cosine similarity computation", logger):
                sim = cosine_similarity(inf_emb, ref_centroid, dim=-1).item()
            logger.debug("Similarity Score: %.3f",sim)

            is_last_attempt = attempt == MAX_RESCANS

            if sim > THRESHOLD + AMBIGUOUS_MARGIN:
                logger.info("Allow")
            
                return True

            elif sim < THRESHOLD - AMBIGUOUS_MARGIN or is_last_attempt:
                logger.info("Rejected")
                return False

            else:
                print("Ambiguous result — rescanning...")
                logger.warning("Ambiguous reselt, attempting rescan")
                attempt += 1
        
        logger.error("Rejected (max rescans reached)")
        return False


if __name__ == "__main__":
    logger.debug(f"Running on device {DEVICE}")
    result = authenticate()