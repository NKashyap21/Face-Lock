# FaceLock

FaceLock is a Linux facial authentication system that integrates with the Pluggable Authentication Modules (PAM) framework to provide passwordless authentication using face recognition.

Unlike traditional implementations that load deep learning models on every authentication request, FaceLock runs as a persistent `systemd` daemon. The daemon keeps all machine learning models loaded in memory and communicates with PAM through a Unix domain socket, significantly reducing authentication latency.

The project uses FaceNet for face embeddings, MTCNN for face detection, and MediaPipe Face Landmarker for blink-based liveness detection.

---

## Features

* Face recognition using FaceNet embeddings
* Blink-based liveness detection
* PAM integration for Linux authentication
* Background daemon managed by `systemd`
* Unix domain socket communication
* Password fallback on authentication failure
* Cached model loading for faster authentication
* Modular architecture

---

## Demo

<p align="center">
  <img src="demo.gif" alt="FaceLock Demo" width="700">
</p>

---

## Architecture

```text
                    systemd
                       │
                       ▼
              FaceLock Daemon
                       │
     ┌─────────────────┴─────────────────┐
     │                                   │
 Load FaceNet                     Load MediaPipe
 Load MTCNN                       Load Reference Embedding
     │
     ▼
Wait on Unix Domain Socket
     │
     ▼
pam_exec (PAM)
     │
     ▼
 PAM Client
     │
     ▼
Authentication Request
     │
     ▼
 Face Detection
     │
     ▼
 Blink Verification
     │
     ▼
 Face Embedding
     │
     ▼
 Cosine Similarity
     │
     ▼
 Authentication Result
```

---

## Project Structure

```text
Face-Lock/
│
├── facelock/
│   ├── authenticate.py
│   ├── camera.py
│   ├── daemon.py
│   ├── embeddings.py
│   ├── enroll.py
│   ├── pam_client.py
│   └── ...
│
├── models/
│   └── face_landmarker.task
│
├── scripts/
│   ├── install.sh
│   ├── uninstall.sh
│   └── facelock-pam
│
├── systemd/
│   └── facelock.service
│
├── storage/
├── README.md
├── LICENSE
├── pyproject.toml
└── uv.lock
```

---

## Requirements

* Linux
* Python 3.11+
* `systemd`
* PAM
* Webcam
* `uv`

Tested on:

* KDE Plasma (Plasma Login)
* Arch Linux / CachyOS

---

## Installation

Clone the repository.

```bash
git clone https://github.com/NKashyap21/Face-Lock.git
cd Face-Lock
```

Run the installer.

```bash
sudo ./scripts/install.sh
```

The installer will:

* Install the project under `/opt/facelock`
* Install the `systemd` service
* Install the PAM helper
* Enable and start the daemon

---

## PAM Configuration

FaceLock integrates through PAM.

Add the following line **before**

```pam
auth include system-login
```

inside your login manager's PAM configuration.

```pam
auth sufficient pam_exec.so quiet /usr/local/bin/facelock-pam
```

For KDE Plasma Login this is typically:

```text
/etc/pam.d/plasmalogin
```

Different desktop environments may use different PAM service files.

---

## Enrolling a Face

After installation, enroll a reference face.

```bash
uv --directory /opt/facelock run python -m facelock.enroll
```

The reference embedding will be stored locally and used for future authentication.

---

## Usage

Check daemon status.

```bash
systemctl status facelock
```

View logs.

```bash
journalctl -u facelock -f
```

Restart the daemon.

```bash
sudo systemctl restart facelock
```

---

## How It Works

1. The FaceLock daemon starts automatically using `systemd`.
2. FaceNet, MTCNN, MediaPipe, and the enrolled embedding are loaded once.
3. The daemon waits for authentication requests on a Unix domain socket.
4. During login, PAM invokes a lightweight client using `pam_exec`.
5. The client requests authentication from the daemon.
6. The daemon captures webcam frames.
7. MTCNN detects the user's face.
8. MediaPipe verifies liveness using blink detection.
9. FaceNet generates a facial embedding.
10. The embedding is compared against the enrolled reference embedding using cosine similarity.
11. On success, PAM grants authentication. Otherwise, the normal password authentication process continues.

---

## Performance

Loading deep learning models dominates the runtime of most facial authentication systems.

FaceLock avoids repeatedly loading models by running as a persistent daemon. Authentication requests only perform face detection, liveness verification, embedding generation, and similarity comparison.

Communication between PAM and the daemon is performed through a Unix domain socket, keeping the authentication path lightweight.

---

## Troubleshooting

Verify that the daemon is running.

```bash
systemctl status facelock
```

Check daemon logs.

```bash
journalctl -u facelock -f
```

Verify that the Unix socket exists.

```bash
ls /run/facelock/
```

Re-enroll your face.

```bash
uv --directory /opt/facelock run python -m facelock.enroll
```

---

## Known Limitations

* Supports a single enrolled user.
* Requires a webcam.
* KDE Wallet may still prompt for its password after biometric login because `pam_kwallet5` does not receive the user's login password.
* Some display managers invoke PAM only after the user initiates authentication (for example, by pressing Enter). In such environments, FaceLock starts when PAM authentication begins rather than when the greeter is first displayed.

---

## Future Work

* Multi-user support
* Adaptive authentication thresholds
* Improved anti-spoofing techniques
* Automatic embedding updates
* Model optimization and quantization
* Support for additional Linux display managers

---

## License

This project is licensed under the MIT License.
