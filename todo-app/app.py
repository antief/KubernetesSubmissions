import os

import uvicorn
from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Todo app"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))

    print(f"Server started in port {port}", flush=True)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
    )
