from facelock.embeddings import load_reference_embedding
from facelock.authenticate import authenticate
import socket 
import os 
import logging

logger = logging.getLogger(__name__)

SOCKET_PATH = "/run/facelock/facelock.sock"

if os.path.exists(SOCKET_PATH):
    os.remove(SOCKET_PATH)

server = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
server.bind(SOCKET_PATH)
os.chmod(SOCKET_PATH, 0o666)
server.listen()

print("Loading reference embeddings...",flush=True)
reference_emb = load_reference_embedding()
print("Finished Loading reference embeddings...",flush=True)

while True:
    print("Waiting for connection...", flush=True)
    conn,addr = server.accept()
    print("Client connected!", flush=True)
    try:
        data = conn.recv(1024)
        print(f"Received: {data!r}", flush=True)
        if data == b"VERIFY":
            res = authenticate(reference_emb)
            print("Calling authenticate()", flush=True)
            if res:
                conn.send(b"SUCCESS")
            else:
                conn.send(b"FAIL")
        else:
            conn.send(b"FAIL")
    finally:
        conn.close()