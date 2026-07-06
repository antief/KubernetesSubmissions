import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse


COUNTER_FILE = Path(
    os.getenv("COUNTER_FILE", "/usr/src/app/files/ping-pong.txt")
)

app = FastAPI()


def read_counter() -> int:
    try:
        return int(COUNTER_FILE.read_text(encoding="utf-8").strip())
    except FileNotFoundError:
        return 0


def write_counter(value: int) -> None:
    COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    COUNTER_FILE.write_text(f"{value}\n", encoding="utf-8")


@app.get("/pingpong", response_class=PlainTextResponse)
def ping_pong() -> str:
    counter = read_counter()
    write_counter(counter + 1)

    return f"pong {counter}"


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
