import os
import time
from pathlib import Path
from urllib.request import urlopen

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse


IMAGE_FILE = Path(
    os.getenv("IMAGE_FILE", "/usr/src/app/files/image.jpg")
)
IMAGE_URL = "https://picsum.photos/1200"
CACHE_SECONDS = 600

app = FastAPI()


def update_image() -> None:
    if (
        IMAGE_FILE.exists()
        and time.time() - IMAGE_FILE.stat().st_mtime < CACHE_SECONDS
    ):
        return

    IMAGE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with urlopen(IMAGE_URL, timeout=30) as response:
        IMAGE_FILE.write_bytes(response.read())


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Todo App</title>
  </head>
  <body>
    <h1>Todo App</h1>
    <img src="/image" alt="Random image" style="max-width: 100%">
  </body>
</html>
"""


@app.get("/image")
def image() -> FileResponse:
    update_image()
    return FileResponse(IMAGE_FILE)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)
