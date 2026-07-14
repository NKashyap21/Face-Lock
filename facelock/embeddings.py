from facenet_pytorch import MTCNN,InceptionResnetV1
from facelock.config import DEVICE,REFERENCE_DIR
from facelock.benchmark import BenchmarkTimer
import torch 
import os 
import logging

logger = logging.getLogger(__name__)

with BenchmarkTimer("Model initialization (FaceNet/MTCNN)", logger):
    mtcnn = MTCNN(device=DEVICE)
    resnet = InceptionResnetV1(pretrained="vggface2").eval().to(DEVICE)

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
        logger.warning(f"Only {len(embeddings)}/{len(images)} valid detections — insufficient")
        return None

    return torch.stack(embeddings).mean(dim=0)

def load_reference_embedding():
    logger.info("Searching For reference embedding...")
    if os.path.exists(f"{REFERENCE_DIR}/referance.pt"):
        logger.info("Found Reference embedding")
        vector = torch.load(os.path.join(REFERENCE_DIR,"referance.pt"),map_location="cpu")
    else:
        logger.critical(f"No reference embedding found in {REFERENCE_DIR}")
        raise RuntimeError(f"No reference embeddings found in {REFERENCE_DIR}")
    
    return vector