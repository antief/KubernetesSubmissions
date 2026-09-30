import os
from pathlib import Path
from urllib.request import urlopen

import uvicorn
from fastapi import FastAPI, HTTPException
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
    "http://ping-pong.exercises.svc.cluster.local/pings",
)

GREETER_URL = os.getenv("GREETER_URL", "http://greeter-svc:8000/")

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
    with urlopen(PING_PONG_URL, timeout=30) as response:
        return int(response.read().decode("utf-8").strip())


def greeting() -> str:
    with urlopen(GREETER_URL, timeout=5) as response:
        return response.read().decode("utf-8").strip()


@app.get("/healthz", response_class=PlainTextResponse)
def healthz() -> str:
    try:
        greeting()
    except (OSError, ValueError) as error:
        raise HTTPException(
            status_code=500,
            detail="A dependent service is unavailable",
        ) from error

    return "ok"


@app.get("/", response_class=PlainTextResponse)
def root() -> str:
    return (
        f"file content: {information_file_content()}\n"
        f"env variable: MESSAGE={MESSAGE}\n"
        f"{latest_log_line()}\n"
        f"Ping / Pongs: {ping_pong_count()}\n"
        f"greetings: {greeting()}\n"
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
