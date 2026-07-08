# Ping-pong

Provides two HTTP endpoints:

- `GET /pingpong` returns the current counter and increments it.
- `GET /pings` returns the current counter without modifying it.

The counter is kept in memory and resets when the Pod restarts.

The application is deployed to the `exercises` namespace.

## Run locally

```bash
PORT=8001 python app.py
```

## Build

```bash
docker build -t ping-pong:2.1 .
```

## Deploy to k3d

From the repository root:

```bash
kubectl apply -f namespaces/exercises.yaml
k3d image import ping-pong:2.1 -c k3s-default
kubectl apply -f ping-pong/manifests/
```

Inspect the resources:

```bash
kubectl get pods,services,ingress -n exercises
```

The endpoint is available at <http://localhost:8081/pingpong>.
