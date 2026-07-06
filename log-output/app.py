import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse


OUTPUT_FILE = Path(
    os.getenv("OUTPUT_FILE", "/usr/src/app/files/output.txt")
)

app = FastAPI()


@app.get("/", response_class=PlainTextResponse)
def root() -> str:
    try:
        return OUTPUT_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "Log output is not available yet.\n"


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
