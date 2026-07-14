from typer import Typer,Exit
from facelock.enroll  import enroll
from facelock.authenticate import authenticate
import sys

app = Typer()

@app.command()
def enroll():
    raise Exit(code=0 if enroll() else 1)

@app.command()
def verify():
    raise Exit(code=0 if authenticate() else 1)

if __name__ == "__main__":
    app()