# Todo app

Displays a random Lorem Picsum image and caches it on a persistent volume for ten minutes.

## Build

`docker build -t todo-app:1.12 .`

## Deploy

From the repository root:

`docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/todo-image`

`docker build -t todo-app:1.12 ./todo-app`

`k3d image import todo-app:1.12 -c k3s-default`

`kubectl apply -f storage/todo-image-persistentvolume.yaml`

`kubectl apply -f todo-app/manifests/`

Open <http://localhost:8081/>.
