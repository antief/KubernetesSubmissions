import os
from datetime import datetime, timezone
from threading import Thread
from time import sleep
from uuid import uuid4

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse


app = FastAPI()
random_string = str(uuid4())


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def current_status() -> str:
    return f"{timestamp()}: {random_string}"


def log_status() -> None:
    while True:
        print(current_status(), flush=True)
        sleep(5)


@app.get("/", response_class=PlainTextResponse)
def root() -> str:
    return current_status()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    Thread(target=log_status, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=port)
