# Todo broadcaster

Consumes Todo creation and update events from NATS and forwards them to a generic HTTP webhook.

All broadcaster replicas use the same NATS queue group, so each event is handled by only one replica. The Deployment runs six replicas.

## Build

```bash
docker build -t broadcaster:4.6 ./broadcaster
```

## NATS

Install NATS with the Prometheus exporter:

```bash
helm repo add nats https://nats-io.github.io/k8s/helm/charts/

helm upgrade --install my-nats nats/nats \
  --version 2.15.0 \
  --namespace nats \
  --create-namespace \
  --set promExporter.enabled=true
```

## Webhook secret

The webhook URL is stored in a SOPS-encrypted Kubernetes Secret.

```bash
export SOPS_AGE_KEY_FILE="$HOME/.config/sops/age/keys.txt"

sops --decrypt \
  broadcaster/manifests/secret.enc.yaml \
  | kubectl apply -f -
```

## Deploy to k3d

```bash
k3d image import broadcaster:4.6 -c k3s-default

kubectl apply \
  -f broadcaster/manifests/deployment.yaml
```
