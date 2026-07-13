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
  -f log-output/manifests/configmap.yaml \
  -f log-output/manifests/deployment.yaml \
  -f log-output/manifests/service.yaml
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

Ping-pong and Log output are exposed through one GKE Gateway and
HTTPRoute. Requests to `/pingpong` are rewritten to `/` before being
forwarded to Ping-pong. The cluster must use the standard Gateway API
channel.

From the repository root:

```bash
gcloud container clusters update dwk-cluster \
  --location=europe-north1-b \
  --gateway-api=standard

kubectl apply -f namespaces/exercises.yaml

kubectl apply \
  -f ping-pong/manifests/postgres.yaml \
  -f ping-pong/manifests/deployment.yaml \
  -f ping-pong/manifests/service.yaml \
  -f log-output/manifests/configmap.yaml \
  -f log-output/manifests/deployment.yaml \
  -f log-output/manifests/service.yaml \
  -f log-output/manifests/gateway.yaml \
  -f log-output/manifests/httproute.yaml

kubectl delete ingress log-output-ingress \
  -n exercises \
  --ignore-not-found

kubectl rollout status \
  deployment/ping-pong-dep \
  -n exercises

kubectl rollout status \
  deployment/log-output-dep \
  -n exercises

kubectl wait \
  --for=condition=Programmed \
  gateway/log-output-gateway \
  -n exercises \
  --timeout=30m
```

Test both routes:

```bash
GATEWAY_IP="$(
  kubectl get gateway log-output-gateway \
    -n exercises \
    -o jsonpath='{.status.addresses[0].value}'
)"

curl --fail --show-error "http://${GATEWAY_IP}/"
curl --fail --show-error "http://${GATEWAY_IP}/pingpong"
```
