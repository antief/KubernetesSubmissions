import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse


app = FastAPI()
counter = 0


@app.get("/pingpong", response_class=PlainTextResponse)
async def ping_pong() -> str:
    global counter

    response = f"pong {counter}"
    counter += 1

    return response


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
