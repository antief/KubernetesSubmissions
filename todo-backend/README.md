# Todo backend

FastAPI backend for the Todo application. Todos are stored in PostgreSQL.

PostgreSQL runs as a single-replica StatefulSet. Database settings are provided through a ConfigMap and a SOPS-encrypted Secret.

## Build

```bash
docker build -t todo-backend:2.8 ./todo-backend
```

## Deploy

```bash
kubectl apply -f namespaces/project.yaml

docker pull postgres:18.0

k3d image import \
  todo-backend:2.8 \
  postgres:18.0 \
  -c k3s-default

export SOPS_AGE_KEY_FILE="$HOME/.config/sops/age/keys.txt"

sops --decrypt \
  todo-backend/manifests/secret.enc.yaml \
  | kubectl apply -f -

kubectl apply \
  -f todo-backend/manifests/configmap.yaml \
  -f todo-backend/manifests/postgres.yaml \
  -f todo-backend/manifests/deployment.yaml \
  -f todo-backend/manifests/service.yaml
```
