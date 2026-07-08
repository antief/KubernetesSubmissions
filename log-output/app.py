import os
from pathlib import Path
from urllib.request import urlopen

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse


OUTPUT_FILE = Path(
    os.getenv("OUTPUT_FILE", "/usr/src/app/files/output.txt")
)

INFORMATION_FILE = Path(
    "/usr/src/app/config/information.txt"
)

MESSAGE = os.environ["MESSAGE"]

PING_PONG_URL = os.getenv(
    "PING_PONG_URL",
    "http://ping-pong-svc:8000/pings",
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


def information_file_content() -> str:
    return INFORMATION_FILE.read_text(
        encoding="utf-8",
    ).strip()


def ping_pong_count() -> int:
    with urlopen(PING_PONG_URL, timeout=5) as response:
        return int(response.read().decode("utf-8").strip())


@app.get("/", response_class=PlainTextResponse)
def root() -> str:
    return (
        f"file content: {information_file_content()}\n"
        f"env variable: MESSAGE={MESSAGE}\n"
        f"{latest_log_line()}\n"
        f"Ping / Pongs: {ping_pong_count()}\n"
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
