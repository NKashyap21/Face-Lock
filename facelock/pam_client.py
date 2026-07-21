import socket
import sys
import traceback

SOCKET_PATH = "/run/facelock/facelock.sock"

try:
    print("Creating socket...")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        print("Connecting...")
        client.connect(SOCKET_PATH)

        print("Connected!")
        client.sendall(b"VERIFY")

        print("Waiting for reply...")
        status = client.recv(1024)

        print(f"Received: {status!r}")

        if status == b"SUCCESS":
            sys.exit(0)
        else:
            sys.exit(1)

except Exception:
    traceback.print_exc()
    sys.exit(1)