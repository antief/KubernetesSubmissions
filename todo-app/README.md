# Todo app

Serves the Todo application HTML, caches the Lorem Picsum image on a persistent volume and communicates with `todo-backend-svc` over HTTP.

The form accepts todos of at most 140 characters. Todo items are fetched from the backend and rendered server-side.

## Build

`docker build -t todo-app:2.2 .`

## Deploy

From the repository root:

`docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/todo-image`

`docker build -t todo-app:2.2 ./todo-app`

`docker build -t todo-backend:2.2 ./todo-backend`

`k3d image import todo-app:2.2 todo-backend:2.2 -c k3s-default`

`kubectl apply -f storage/todo-image-persistentvolume.yaml`

`kubectl apply -f todo-backend/manifests/`

`kubectl apply -f todo-app/manifests/`

Open <http://localhost:8081/>.
