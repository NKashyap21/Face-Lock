#!/usr/bin/env bash

set -e

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root."
    exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
    echo "uv is not installed."
    exit 1
fi

echo "Installing FaceLock..."

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

INSTALL_DIR="/opt/facelock"

rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

cp -r "$REPO_ROOT"/* "$INSTALL_DIR"

cd "$INSTALL_DIR"

uv sync

cat >/etc/systemd/system/facelock.service <<EOF
[Unit]
Description=FaceLock Authentication Daemon
After=multi-user.target

[Service]
Type=simple

WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/uv run python -m facelock.daemon

Restart=on-failure
RestartSec=3

RuntimeDirectory=facelock
RuntimeDirectoryMode=0755

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

cat >/usr/local/bin/facelock-pam <<EOF
#!/bin/sh
exec /usr/bin/uv --directory "$INSTALL_DIR" run python -m facelock.pam_client
EOF

chmod +x /usr/local/bin/facelock-pam

systemctl daemon-reload
systemctl enable facelock
systemctl restart facelock

echo
echo "Installation complete."
echo
echo "Next steps:"
echo
echo "1. Enroll your face:"
echo "   uv --directory $INSTALL_DIR run python -m facelock.enroll"
echo
echo "2. Edit your PAM configuration."
echo
echo "Add the following line BEFORE:"
echo "    auth include system-login"
echo
echo "auth sufficient pam_exec.so quiet /usr/local/bin/facelock-pam"
echo
echo "Then reboot."