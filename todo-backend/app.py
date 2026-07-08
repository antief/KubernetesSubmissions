import os

import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])


class TodoCreate(BaseModel):
    content: str = Field(min_length=1, max_length=140)


todos: list[str] = [
    "Learn Kubernetes",
    "Build a todo application",
]

app = FastAPI()


@app.get("/todos", response_model=list[str])
def get_todos() -> list[str]:
    return todos


@app.post(
    "/todos",
    response_model=str,
    status_code=status.HTTP_201_CREATED,
)
def create_todo(todo: TodoCreate) -> str:
    content = todo.content.strip()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Todo must not be empty",
        )

    todos.append(content)
    return content


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
