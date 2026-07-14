import torch 
from pathlib import Path

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

PROJECT_ROOT = Path(__file__).resolve().parent

REFERENCE_DIR = f"{PROJECT_ROOT}/storage/referance"
THRESHOLD = 0.6
AMBIGUOUS_MARGIN = 0.05
MAX_RESCANS = 2
FRAMES_PER_ATTEMPT = 20
MIN_VALID_DETECTIONS = 3


EAR_THRESHOLD = 0.25          # below this = eye considered closed
MIN_CONSECUTIVE_FRAMES = 1  # frames required to confirm "closed" state (tune later)
FACE_LANDMARKER_MODEL_PATH=f"{PROJECT_ROOT}/models/face_landmarker.task"