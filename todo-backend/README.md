# Todo backend

Stores todos in memory and exposes two HTTP endpoints:

- `GET /todos` returns all todos.
- `POST /todos` creates a todo.

The in-memory data resets when the Pod restarts.

The application is deployed to the `project` namespace and is accessed internally through `todo-backend-svc`.

The bind address and port are passed to the Pod as environment variables in the Deployment.

## Build

```bash
docker build -t todo-backend:2.6 .
```

## Deploy to k3d

From the repository root:

```bash
kubectl apply -f namespaces/project.yaml

docker build \
  -t todo-backend:2.6 \
  ./todo-backend

k3d image import \
  todo-backend:2.6 \
  -c k3s-default

kubectl apply \
  -f todo-backend/manifests/
```

Inspect the resources:

```bash
kubectl get deployments,pods,services \
  -n project
```
