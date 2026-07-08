import json
import os
import time
from html import escape
from pathlib import Path
from typing import Annotated
from urllib.request import Request, urlopen

import uvicorn
from fastapi import FastAPI, Form, HTTPException, status
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse


HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])

IMAGE_FILE = Path(os.environ["IMAGE_FILE"])
IMAGE_URL = os.environ["IMAGE_URL"]
IMAGE_CACHE_SECONDS = int(os.environ["IMAGE_CACHE_SECONDS"])
IMAGE_REQUEST_TIMEOUT_SECONDS = float(
    os.environ["IMAGE_REQUEST_TIMEOUT_SECONDS"]
)

TODO_BACKEND_URL = os.environ["TODO_BACKEND_URL"].rstrip("/")
BACKEND_REQUEST_TIMEOUT_SECONDS = float(
    os.environ["BACKEND_REQUEST_TIMEOUT_SECONDS"]
)

app = FastAPI()


def update_image() -> None:
    if (
        IMAGE_FILE.exists()
        and time.time() - IMAGE_FILE.stat().st_mtime
        < IMAGE_CACHE_SECONDS
    ):
        return

    IMAGE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with urlopen(
        IMAGE_URL,
        timeout=IMAGE_REQUEST_TIMEOUT_SECONDS,
    ) as response:
        IMAGE_FILE.write_bytes(response.read())


def fetch_todos() -> list[str]:
    with urlopen(
        f"{TODO_BACKEND_URL}/todos",
        timeout=BACKEND_REQUEST_TIMEOUT_SECONDS,
    ) as response:
        return json.load(response)


def send_todo(content: str) -> None:
    payload = json.dumps({"content": content}).encode("utf-8")

    request = Request(
        f"{TODO_BACKEND_URL}/todos",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(
        request,
        timeout=BACKEND_REQUEST_TIMEOUT_SECONDS,
    ) as response:
        response.read()


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    todo_items = "\n".join(
        f"        <li>{escape(todo)}</li>"
        for todo in fetch_todos()
    )

    return f"""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Todo App</title>
  </head>
  <body>
    <main>
      <h1>Todo App</h1>

      <img
        src="/image"
        alt="Random image"
        style="max-width: 100%"
      >

      <h2>Add a todo</h2>

      <form action="/todos" method="post">
        <input
          type="text"
          id="content"
          name="content"
          maxlength="140"
          placeholder="Write a todo"
          required
        >
        <button type="submit">Create todo</button>
      </form>

      <h2>Todos</h2>

      <ul>
{todo_items}
      </ul>
    </main>
  </body>
</html>
"""


@app.post("/todos")
def create_todo(
    content: Annotated[
        str,
        Form(min_length=1, max_length=140),
    ],
) -> RedirectResponse:
    clean_content = content.strip()

    if not clean_content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Todo must not be empty",
        )

    send_todo(clean_content)

    return RedirectResponse(
        url="/",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.get("/image")
def image() -> FileResponse:
    update_image()
    return FileResponse(IMAGE_FILE)


if __name__ == "__main__":
    print(f"Server started in port {PORT}", flush=True)
    uvicorn.run(app, host=HOST, port=PORT)
