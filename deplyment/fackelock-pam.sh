#!/bin/bash

# Example PAM wrapper for FaceLock

export HOME=/home/<USERNAME>

exec /path/to/facelock/.venv/bin/facelock verify