# Log output

The application runs as two containers in a single Kubernetes Pod.

- `log-output-writer` generates one UUID on startup and writes it with a UTC timestamp every five seconds.
- `log-output-reader` exposes the latest log line through HTTP.
- The containers share the log file through an `emptyDir` volume.
- The reader fetches the Ping-pong counter from `ping-pong-svc`.
- A ConfigMap provides the `MESSAGE` environment variable and the mounted `information.txt` file.

The application is deployed to the `exercises` namespace.

## Build

```bash
docker build -t log-output:2.5 .
```

## Deploy to k3d

From the repository root:

```bash
kubectl apply -f namespaces/exercises.yaml

docker build \
  -t log-output:2.5 \
  ./log-output

k3d image import \
  log-output:2.5 \
  -c k3s-default

kubectl apply \
  -f log-output/manifests/
```

Inspect the resources:

```bash
kubectl get deployments,pods,services,configmaps \
  -n exercises
```

Test the output:

```bash
kubectl exec \
  -n exercises \
  deployment/log-output-dep \
  -c log-output-reader \
  -- python -c '
from urllib.request import urlopen

with urlopen(
    "http://localhost:8000/",
    timeout=5,
) as response:
    print(response.read().decode(), end="")
'
```
