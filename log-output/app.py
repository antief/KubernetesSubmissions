import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse


OUTPUT_FILE = Path(
    os.getenv("OUTPUT_FILE", "/usr/src/app/files/output.txt")
)

PING_PONG_FILE = Path(
    os.getenv("PING_PONG_FILE", "/usr/src/app/files/ping-pong.txt")
)

app = FastAPI()


def latest_log_line() -> str:
    try:
        lines = OUTPUT_FILE.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return "Log output is not available yet."

    if not lines:
        return "Log output is not available yet."

    return lines[-1]


def ping_pong_count() -> int:
    try:
        return int(PING_PONG_FILE.read_text(encoding="utf-8").strip())
    except FileNotFoundError:
        return 0


@app.get("/", response_class=PlainTextResponse)
def root() -> str:
    return (
        f"{latest_log_line()}\n"
        f"Ping / Pongs: {ping_pong_count()}\n"
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
