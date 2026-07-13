# FaceLock

A face authentication system for Linux, built end-to-end: webcam capture → face detection & alignment → embedding extraction → liveness verification → identity matching.

---

## Problem Statement

Most personal face-auth tutorials stop at "detect a face and compare embeddings." FaceLock goes further by treating this as a full system with the failure modes that matter in practice: ambiguous match scores, unreliable single-shot captures, and the fact that a bare embedding comparison can be fooled by a photo held up to the camera. The goal was to understand and build every non-trivial component of that pipeline, not just wire together a demo.

---

## Architecture

```
                    Webcam
                       │
                       ▼
              Frame Capture (OpenCV)
                       │
                       ▼
        ┌──────────────┴──────────────┐
        ▼                             ▼
   Liveness Check                Face Detection & Alignment
  (MediaPipe FaceLandmarker            (MTCNN)
   + Eye Aspect Ratio)                     │
        │                                  ▼
        │                          Embedding Extraction
        │                        (InceptionResnetV1, vggface2)
        │                                  │
        └──────────────┬───────────────────┘
                        ▼
              Cosine Similarity vs.
              Reference Centroid
                        │
          ┌─────────────┼─────────────┐
          ▼              ▼             ▼
       Allow         Ambiguous      Rejected
                    (rescan, up
                     to max retries)
```

Liveness and identity checks run independently on the same set of captured frames. Both must pass — a genuine blink pattern **and** a similarity score above threshold — before authentication succeeds.

---

## Components

| Component | Library | Purpose |
|---|---|---|
| Frame capture | OpenCV (`cv2.VideoCapture`) | Grabs a burst of frames from the webcam per attempt |
| Face detection & alignment | `facenet-pytorch` (MTCNN) | Finds the face, aligns it using 5-point landmarks before embedding |
| Face embedding | `facenet-pytorch` (InceptionResnetV1, pretrained on VGGFace2) | Produces a 512-dimensional identity vector per face |
| Liveness detection | `mediapipe` (FaceLandmarker task) | Extracts eye contour landmarks; computes Eye Aspect Ratio (EAR) to detect a genuine blink |
| Similarity scoring | PyTorch (`cosine_similarity`) | Compares live embedding(s) against a stored reference centroid |

---

## Project Structure

```
FaceLock/
├── test/
│   ├── referance/       # enrolled reference images
│   └── inference/       # temporary captures during authentication
├── models/
│   └── face_landmarker.task   # MediaPipe model (not committed — see Setup)
├── helpers.py           # shared config, models, capture/embedding/liveness functions
├── enroll.py            # enrollment flow (replace/add/cancel existing reference)
├── authenticate.py       # authentication flow with liveness + identity gates
└── README.md
```

---

## Setup

**1. Install dependencies**
```bash
uv sync
```

**2. Download the MediaPipe Face Landmarker model** (not committed to the repo — see `.gitignore`)
```bash
mkdir -p models
curl -L -o models/face_landmarker.task https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task
```

**3. Confirm webcam access**
```bash
ls /dev/video*
```
If you hit a permissions error, add your user to the `video` group and re-login:
```bash
sudo usermod -aG video $USER
```

**4. Enroll a reference identity**
```bash
python enroll.py
```
Follow the prompt — blink naturally during capture. A live blink is required; enrollment rejects static-photo captures.

**5. Authenticate**
```bash
python authenticate.py
```

---

## Calibration

Thresholds below were tuned empirically against real test data, not textbook defaults:

- **Similarity threshold: 0.6** — validated against sibling-vs-self and celebrity-pair test cases (genuine matches landed 0.85–0.89; impostor/sibling matches landed 0.12–0.52).
- **Ambiguous margin: ±0.05** — scores within this band of the threshold trigger a rescan rather than an outright allow/reject.
- **Max rescans: 2** — after this, the last result stands as final (no infinite retry loop).
- **EAR threshold: 0.25** — open-eye EAR typically sits ~0.27–0.30; genuine blinks dip to ~0.20–0.24 based on personal calibration testing.
- **Frames per attempt: 20** — increased from an initial 5 after testing showed too few frames unreliably captured a natural blink within the capture window.

If you re-run calibration on your own hardware/lighting, log the actual score distributions rather than trusting these numbers blindly — they're specific to the conditions they were tuned under.

---


## Known Limitations (v1)

- **Liveness detection defeats still-photo spoofing only.** The blink-based EAR check catches someone holding up a printed photo or a static image on a screen, but a **video replay attack** (playing a recording of the enrolled user blinking) would currently pass. Proper anti-spoofing (texture/depth analysis, challenge-response) is planned for v2.
- **Threshold values are tuned to one person's face, camera, and lighting conditions.** They are a reasonable starting point, not a validated universal constant — recalibrate before relying on this for anyone else.
- **No handling for extreme lighting or multiple simultaneous faces during authentication** (multi-face handling exists for enrollment data separation, not for rejecting bystanders during a live auth attempt).
- **Reference set can be small.** Enrollment works with as few as one photo; more enrollment captures across different conditions (angles, lighting) will make the reference centroid more robust.

---

## Tech Stack

- **ML/CV:** PyTorch, `facenet-pytorch` (MTCNN, InceptionResnetV1), `mediapipe` (FaceLandmarker)
- **Vision utilities:** OpenCV, Pillow
- **Platform:** Linux (developed on CachyOS)