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

## Deploy to GKE

Ping-pong and Log output are exposed through one GKE Ingress. The
application images are stored in Google Artifact Registry.

From the repository root:

```bash
export REGISTRY="europe-north1-docker.pkg.dev/dwk-gke-antti-6c49/dwk-images"

docker build \
  -t "${REGISTRY}/ping-pong:3.2" \
  ./ping-pong

docker build \
  -t "${REGISTRY}/log-output:2.5" \
  ./log-output

docker push "${REGISTRY}/ping-pong:3.2"
docker push "${REGISTRY}/log-output:2.5"

kubectl apply -f namespaces/exercises.yaml

kubectl apply \
  -f ping-pong/manifests/postgres.yaml \
  -f ping-pong/manifests/deployment.yaml \
  -f ping-pong/manifests/service.yaml \
  -f log-output/manifests/configmap.yaml \
  -f log-output/manifests/deployment.yaml \
  -f log-output/manifests/service.yaml \
  -f log-output/manifests/ingress.yaml

kubectl rollout status \
  deployment/ping-pong-dep \
  -n exercises

kubectl rollout status \
  deployment/log-output-dep \
  -n exercises
```

Wait for the Ingress address:

```bash
kubectl get ingress log-output-ingress \
  -n exercises \
  --watch
```

Test both routes:

```bash
INGRESS_IP="$(
  kubectl get ingress log-output-ingress \
    -n exercises \
    -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
)"

curl --fail --show-error "http://${INGRESS_IP}/"
curl --fail --show-error "http://${INGRESS_IP}/pingpong"
```
