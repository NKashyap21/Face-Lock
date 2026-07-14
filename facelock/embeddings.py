from facenet_pytorch import MTCNN,InceptionResnetV1
from facelock.config import DEVICE,REFERENCE_DIR
import torch 
import os 

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
        print(f"Only {len(embeddings)}/{len(images)} valid detections — insufficient")
        return None

    return torch.stack(embeddings).mean(dim=0)

def load_reference_embedding():
    if os.path.exists(f"{REFERENCE_DIR}/referance.pt"):
        vector = torch.load(os.path.join(REFERENCE_DIR,"referance.pt"),map_location="cpu")
    else:
        raise RuntimeError(f"No reference embeddings found in {REFERENCE_DIR}")
    
    return vector