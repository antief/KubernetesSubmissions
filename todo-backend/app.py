import logging
import os
from contextlib import asynccontextmanager

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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("todo-backend")


class TodoCreate(BaseModel):
    content: str = Field(min_length=1, max_length=140)


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
                content VARCHAR(140) NOT NULL
            )
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
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/todos", response_model=list[str])
def get_todos() -> list[str]:
    with connect_to_database() as connection:
        rows = connection.execute(
            """
            SELECT content
            FROM todos
            ORDER BY id
            """
        ).fetchall()

    return [row[0] for row in rows]


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

    return content


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
