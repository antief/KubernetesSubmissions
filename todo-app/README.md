# Todo app

Serves the Todo application HTML, caches the Lorem Picsum image on a persistent volume and communicates with `todo-backend-svc` over HTTP.

The form accepts todos of at most 140 characters. Todo items are fetched from the backend and rendered server-side.

The application is deployed to the `project` namespace.

Runtime URLs, ports, paths and timeout values are passed to the Pod as environment variables in the Deployment.

## Build

```bash
docker build -t todo-app:2.6 .
```

## Deploy to k3d

From the repository root:

```bash
kubectl apply -f namespaces/project.yaml

docker exec \
  k3d-k3s-default-agent-0 \
  mkdir -p /tmp/todo-image

docker build -t todo-app:2.6 ./todo-app
docker build -t todo-backend:2.6 ./todo-backend

k3d image import \
  todo-app:2.6 \
  todo-backend:2.6 \
  -c k3s-default

kubectl apply \
  -f storage/todo-image-persistentvolume.yaml

kubectl apply \
  -f todo-backend/manifests/

kubectl apply \
  -f todo-app/manifests/
```

Inspect the project resources:

```bash
kubectl get deployments,pods,services,ingress,pvc \
  -n project
```

Open <http://localhost:8081/>.
