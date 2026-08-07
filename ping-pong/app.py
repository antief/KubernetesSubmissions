import os

import psycopg
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse


DATABASE_URL = os.environ["DATABASE_URL"]

app = FastAPI()


def initialize_database() -> None:
    with psycopg.connect(DATABASE_URL) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS ping_pong_counter (
                id SMALLINT PRIMARY KEY,
                value BIGINT NOT NULL
            )
            """
        )

        connection.execute(
            """
            INSERT INTO ping_pong_counter (id, value)
            VALUES (1, 0)
            ON CONFLICT (id) DO NOTHING
            """
        )


@app.get("/healthz", response_class=PlainTextResponse)
def healthz() -> str:
    try:
        initialize_database()
    except psycopg.Error as error:
        raise HTTPException(
            status_code=500,
            detail="Database is unavailable",
        ) from error

    return "ok"


@app.get("/", response_class=PlainTextResponse)
def ping_pong() -> str:
    initialize_database()

    with psycopg.connect(DATABASE_URL) as connection:
        row = connection.execute(
            """
            UPDATE ping_pong_counter
            SET value = value + 1
            WHERE id = 1
            RETURNING value
            """
        ).fetchone()

    if row is None:
        raise RuntimeError("Ping-pong counter row is missing")

    current = row[0] - 1
    return f"pong {current}"


@app.get("/pings", response_class=PlainTextResponse)
def pings() -> str:
    initialize_database()

    with psycopg.connect(DATABASE_URL) as connection:
        row = connection.execute(
            """
            SELECT value
            FROM ping_pong_counter
            WHERE id = 1
            """
        ).fetchone()

    if row is None:
        raise RuntimeError("Ping-pong counter row is missing")

    return str(row[0])


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
