# Ping-pong

Responds to `/pingpong` with a request counter.

The counter is stored in a file on a persistent volume shared with the Log output application.

## Run locally

```bash
mkdir -p /tmp/ping-pong
COUNTER_FILE=/tmp/ping-pong/ping-pong.txt PORT=8000 python app.py
```

## Build

```bash
docker build -t ping-pong:1.11 .
```

## Deploy to k3d

From the repository root:

```bash
k3d image import ping-pong:1.11 -c k3s-default
kubectl apply -f storage/
kubectl apply -f ping-pong/manifests/
```
