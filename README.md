# FaceLock 

A Linux facial authentication system built using **FaceNet**, **MTCNN**, **MediaPipe**, and the **Linux PAM (Pluggable Authentication Modules)** framework.

FaceLock provides secure biometric authentication through facial recognition with blink-based liveness detection and integrates directly into the Linux desktop login process.

---

## Features

- Face verification using FaceNet (InceptionResnetV1)
- Face detection and alignment using MTCNN
- Blink-based liveness detection using MediaPipe Face Landmarker
- Multi-frame embedding aggregation for improved robustness
- Linux CLI built with Typer
- Integrated with Linux PAM for desktop authentication
- Password fallback on failed authentication
- Structured logging
- Built-in performance benchmarking

---

## Authentication Pipeline

```
                Webcam
                   │
                   ▼
         Capture 20 RGB Frames
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
 MediaPipe             MTCNN + FaceNet
Liveness Check          Face Embeddings
        │                     │
        └──────────┬──────────┘
                   ▼
        Average Face Embedding
                   │
                   ▼
        Cosine Similarity Match
                   │
         ┌─────────┴─────────┐
         │                   │
     Match Found        Authentication Failed
         │                   │
         ▼                   ▼
 Linux PAM Success      Password Fallback
```

---

## Linux PAM Integration

FaceLock exposes a simple CLI:

```bash
facelock verify
```

The command returns:

| Exit Code | Meaning |
|-----------|---------|
| `0` | Authentication successful |
| Non-zero | Authentication failed |

The Linux PAM framework executes FaceLock using `pam_exec.so` during authentication.

```
User
 │
 ▼
Plasma Login
 │
 ▼
PAM
 │
 ▼
pam_exec.so
 │
 ▼
FaceLock CLI
 │
 ▼
Face Verification
 │
 ▼
Exit Code
 │
 ├── 0 → Login Successful
 └── 1 → Password Authentication
```

Authentication is initiated when the user starts the login process (e.g., pressing **Enter** on the Plasma Login screen).

---

## Liveness Detection

FaceLock performs blink-based liveness detection before facial verification.

For every captured frame:

- Detect facial landmarks using MediaPipe
- Compute Eye Aspect Ratio (EAR)
- Detect a valid blink sequence
- Reject authentication if liveness verification fails

This helps mitigate simple presentation attacks using photographs.

---

## Multi-frame Recognition

Instead of authenticating using a single image, FaceLock:

1. Captures multiple frames
2. Generates a FaceNet embedding for each frame
3. Computes the average embedding
4. Compares against the enrolled reference embedding

This significantly improves robustness under:

- Lighting variation
- Minor pose changes
- Camera noise
- Facial expression changes

---

## Performance

Typical authentication timings on an Intel Core Ultra laptop:

| Stage | Time |
|--------|------|
| Reference embedding loading | ~0.002 s |
| Camera capture | ~4.36 s |
| Liveness detection | ~0.38–0.80 s |
| Face embedding generation | ~1.1–3.3 s |
| Cosine similarity | <1 ms |
| Total authentication | ~5.9–8.4 s |

---

## CLI

Enroll a new user:

```bash
facelock enroll
```

Verify identity:

```bash
facelock verify
```


---

## Project Structure

```
facelock/
│
├── cli.py
├── authenticate.py
├── enroll.py
├── camera.py
├── embeddings.py
├── liveness.py
├── storage.py
├── config.py
│
├── models/
│   └── face_landmarker.task
│
└── storage/
```

---

## Technologies

- Python
- PyTorch
- FaceNet (InceptionResnetV1)
- MTCNN
- MediaPipe Face Landmarker
- OpenCV
- Typer
- Linux PAM
- NumPy

---

## Future Improvements

- Persistent authentication daemon (`facelockd`) to eliminate model loading latency
- Multi-user enrollment
- Configurable authentication thresholds
- Automatic benchmark mode
- Wayland lock screen integration
- Support for ArcFace / InsightFace backends

---

## Motivation

FaceLock was developed to explore the intersection of:

- Computer Vision
- Deep Learning
- Linux Systems Programming
- Authentication Systems

Rather than building a standalone facial recognition application, the goal was to integrate a complete facial authentication pipeline directly into the Linux authentication framework using PAM.

---

## Disclaimer

FaceLock is intended for research and educational purposes.

While it implements blink-based liveness detection and biometric verification, it has not undergone formal security auditing and should not be considered a replacement for enterprise-grade authentication solutions.