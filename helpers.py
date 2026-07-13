import os
import glob
import shutil
import time
import cv2
import torch
from PIL import Image
from torch.nn.functional import cosine_similarity
from facenet_pytorch import MTCNN, InceptionResnetV1

# ---------- Config ----------
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
REFERENCE_DIR = "test/referance"
INFERENCE_DIR = "test/inference"

THRESHOLD = 0.6
AMBIGUOUS_MARGIN = 0.05
MAX_RESCANS = 2
FRAMES_PER_ATTEMPT = 5
MIN_VALID_DETECTIONS = 3

# ---------- Models (loaded once, shared by both scripts) ----------
mtcnn = MTCNN(device=DEVICE)
resnet = InceptionResnetV1(pretrained="vggface2").eval().to(DEVICE)


def clear_dir(path):
    os.makedirs(path, exist_ok=True)
    for f in glob.glob(os.path.join(path, "*")):
        os.remove(f)


def capture_frames(num_frames, save_dir):
    """Capture frames from webcam, save to save_dir, return list of PIL Images."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")

    frames = []
    os.makedirs(save_dir, exist_ok=True)
    count = 0
    while count < num_frames:
        ret, frame = cap.read()
        if not ret:
            continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        frames.append(img)

        timestamp = int(time.time() * 1000)
        img.save(os.path.join(save_dir, f"capture_{timestamp}.jpg"))

        count += 1
        time.sleep(0.2)

    cap.release()
    return frames


def get_averaged_embedding(images, min_valid=1):
    """Run MTCNN + resnet on a list of PIL images, average valid embeddings."""
    embeddings = []
    for img in images:
        face = mtcnn(img)
        if face is None:
            continue
        with torch.no_grad():
            emb = resnet(face.unsqueeze(0).to(DEVICE))
        embeddings.append(emb.squeeze(0))

    if len(embeddings) < min_valid:
        print(f"Only {len(embeddings)}/{len(images)} valid detections — insufficient")
        return None

    return torch.stack(embeddings).mean(dim=0)


def load_reference_centroid():
    """Compute the averaged reference embedding from the referance folder."""
    ref_files = glob.glob(os.path.join(REFERENCE_DIR, "*"))
    if not ref_files:
        raise RuntimeError(f"No reference images found in {REFERENCE_DIR}")

    ref_images = [Image.open(f).convert("RGB") for f in ref_files]
    ref_emb = get_averaged_embedding(ref_images, min_valid=1)
    if ref_emb is None:
        raise RuntimeError("Could not extract any valid face from reference images")
    return ref_emb


def promote_inference_to_reference():
    """After a successful authentication, replace reference images with the
    latest inference captures (keeps enrollment fresh over time)."""
    clear_dir(REFERENCE_DIR)
    for f in glob.glob(os.path.join(INFERENCE_DIR, "*")):
        shutil.copy(f, REFERENCE_DIR)
    print("Reference images updated with latest successful authentication captures.")