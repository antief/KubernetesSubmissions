import json
import logging
import os
from contextlib import asynccontextmanager

import nats
import psycopg
import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel, Field, ValidationError


HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])

POSTGRES_HOST = os.environ["POSTGRES_HOST"]
POSTGRES_PORT = int(os.environ["POSTGRES_PORT"])
POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]

NATS_URL = os.environ["NATS_URL"]
NATS_SUBJECT = "todos.events"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("todo-backend")

is_healthy = True


class TodoCreate(BaseModel):
    content: str = Field(min_length=1, max_length=140)


class Todo(BaseModel):
    id: int
    content: str
    done: bool


def connect_to_database():
    return psycopg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )


def initialize_database() -> None:
    with connect_to_database() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id BIGSERIAL PRIMARY KEY,
                content VARCHAR(140) NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )
            """
        )

        connection.execute(
            """
            ALTER TABLE todos
            ADD COLUMN IF NOT EXISTS done BOOLEAN NOT NULL DEFAULT FALSE
            """
        )

        connection.execute(
            """
            INSERT INTO todos (content)
            SELECT seed.content
            FROM (
                VALUES (%s), (%s)
            ) AS seed(content)
            WHERE NOT EXISTS (
                SELECT 1
                FROM todos
            )
            """,
            (
                "Learn Kubernetes",
                "Build a todo application",
            ),
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    app.state.nats = await nats.connect(NATS_URL)

    try:
        yield
    finally:
        await app.state.nats.drain()


app = FastAPI(lifespan=lifespan)


async def publish_todo_event(message: str) -> None:
    payload = json.dumps(
        {
            "message": message,
        }
    ).encode()

    await app.state.nats.publish(
        NATS_SUBJECT,
        payload,
    )
    await app.state.nats.flush()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    if not is_healthy:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Application is unhealthy",
        )

    try:
        with connect_to_database() as connection:
            connection.execute("SELECT 1")
    except psycopg.Error as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database is unavailable",
        ) from error

    return {"status": "ok"}


@app.post("/break")
def break_app() -> dict[str, str]:
    global is_healthy
    is_healthy = False
    return {"status": "broken"}


@app.get("/todos", response_model=list[Todo])
def get_todos() -> list[Todo]:
    with connect_to_database() as connection:
        rows = connection.execute(
            """
            SELECT id, content, done
            FROM todos
            ORDER BY id
            """
        ).fetchall()

    return [
        Todo(
            id=row[0],
            content=row[1],
            done=row[2],
        )
        for row in rows
    ]


@app.put("/todos/{todo_id}", response_model=Todo)
async def mark_todo_done(todo_id: int) -> Todo:
    with connect_to_database() as connection:
        row = connection.execute(
            """
            UPDATE todos
            SET done = TRUE
            WHERE id = %s
            RETURNING id, content, done
            """,
            (todo_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    todo = Todo(
        id=row[0],
        content=row[1],
        done=row[2],
    )

    await publish_todo_event("A todo was updated")

    return todo


@app.post(
    "/todos",
    response_model=str,
    status_code=status.HTTP_201_CREATED,
)
async def create_todo(request: Request) -> str:
    payload = await request.json()
    raw_content = payload.get("content")

    logger.info("todo_request content=%r", raw_content)

    try:
        todo = TodoCreate.model_validate(payload)
    except ValidationError as error:
        logger.warning(
            "todo_rejected content=%r reason=validation_error",
            raw_content,
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=error.errors(),
        ) from error

    content = todo.content.strip()

    if not content:
        logger.warning(
            "todo_rejected content=%r reason=empty",
            raw_content,
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Todo must not be empty",
        )

    with connect_to_database() as connection:
        connection.execute(
            """
            INSERT INTO todos (content)
            VALUES (%s)
            """,
            (content,),
        )

    logger.info("todo_created content=%r", content)

    await publish_todo_event("A todo was created")

    return content


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
