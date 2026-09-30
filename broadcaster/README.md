# Todo broadcaster

Consumes Todo creation and update events from NATS. Production forwards them to a generic HTTP webhook; staging logs them without forwarding.

All broadcaster replicas use the same NATS queue group on their environment-specific subject, so each event is handled by only one replica. The Deployment runs six replicas.

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

The production webhook URL is stored in a SOPS-encrypted Kubernetes Secret. Staging needs no webhook credential.

```bash
export SOPS_AGE_KEY_FILE="$HOME/.config/sops/age/keys.txt"

sops --decrypt \
  broadcaster/manifests/secret.enc.yaml \
  | sed "s/namespace: project/namespace: production/" \
  | kubectl apply -n production -f -
```

## Deployment

Both environment overlays include the broadcaster Deployment. GitHub Actions publishes its image to GHCR and Argo CD deploys it alongside the Todo application. See the Todo app README for GitOps setup.
