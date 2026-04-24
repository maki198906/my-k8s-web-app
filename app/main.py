import socket

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "Hello from Kubernetes + FastAPI",
        "hostname": socket.gethostname(),
    }
