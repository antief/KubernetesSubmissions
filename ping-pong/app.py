import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse


counter = 0

app = FastAPI()


@app.get("/pingpong", response_class=PlainTextResponse)
def ping_pong() -> str:
    global counter

    current = counter
    counter += 1

    return f"pong {current}"


@app.get("/pings", response_class=PlainTextResponse)
def pings() -> str:
    return str(counter)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
