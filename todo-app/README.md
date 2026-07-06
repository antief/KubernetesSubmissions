# Todo app

Displays a cached Lorem Picsum image, a 140-character todo input, a send button and a hardcoded todo list.

## Build

`docker build -t todo-app:1.13 .`

## Deploy

From the repository root:

`docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/todo-image`

`docker build -t todo-app:1.13 ./todo-app`

`k3d image import todo-app:1.13 -c k3s-default`

`kubectl apply -f storage/todo-image-persistentvolume.yaml`

`kubectl apply -f todo-app/manifests/`

Open <http://localhost:8081/>.
