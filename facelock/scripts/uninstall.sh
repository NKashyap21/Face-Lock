#!/usr/bin/env bash

set -e

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root."
    exit 1
fi

echo "Stopping FaceLock..."

systemctl stop facelock 2>/dev/null || true
systemctl disable facelock 2>/dev/null || true

rm -f /etc/systemd/system/facelock.service
rm -f /usr/local/bin/facelock-pam

systemctl daemon-reload

rm -rf /opt/facelock

echo
echo "FaceLock has been removed."
echo
echo "Please remove the following line from your PAM configuration:"
echo
echo "auth sufficient pam_exec.so quiet /usr/local/bin/facelock-pam"