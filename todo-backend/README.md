# Todo backend

Stores todos in memory and exposes two HTTP endpoints:

- `GET /todos` returns all todos.
- `POST /todos` creates a todo.

The in-memory data resets when the Pod restarts.

## Build

`docker build -t todo-backend:2.2 .`

## Deploy

From the repository root:

`docker build -t todo-backend:2.2 ./todo-backend`

`k3d image import todo-backend:2.2 -c k3s-default`

`kubectl apply -f todo-backend/manifests/`
