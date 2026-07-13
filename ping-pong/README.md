# Ping-pong

Provides two HTTP endpoints:

- `GET /` returns the current counter and increments it.
- `GET /pings` returns the current counter without modifying it.

The counter is stored in PostgreSQL.

PostgreSQL runs as a single-replica StatefulSet using the cluster's default StorageClass. The application and database are deployed to the `exercises` namespace.

## Build

```bash
docker build \
  -t europe-north1-docker.pkg.dev/dwk-gke-antti-6c49/dwk-images/ping-pong:3.4 \
  .
```

## Deploy to k3d

From the repository root:

```bash
kubectl apply -f namespaces/exercises.yaml

docker build \
  -t europe-north1-docker.pkg.dev/dwk-gke-antti-6c49/dwk-images/ping-pong:3.4 \
  ./ping-pong

docker pull docker.io/library/postgres:18.0

k3d image import \
  europe-north1-docker.pkg.dev/dwk-gke-antti-6c49/dwk-images/ping-pong:3.4 \
  docker.io/library/postgres:18.0 \
  -c k3s-default

kubectl apply \
  -f ping-pong/manifests/postgres.yaml

kubectl rollout status \
  statefulset/ping-pong-postgres \
  -n exercises

kubectl apply \
  -f ping-pong/manifests/deployment.yaml \
  -f ping-pong/manifests/service.yaml

kubectl rollout status \
  deployment/ping-pong-dep \
  -n exercises
```

Inspect the resources:

```bash
kubectl get deployment,statefulset,pods,services,pvc \
  -n exercises
```

Test the endpoint:

```bash
kubectl port-forward \
  -n exercises \
  service/ping-pong-svc \
  8081:80
```

In another terminal:

```bash
curl --fail --show-error http://localhost:8081/
```

Inspect the stored counter:

```bash
kubectl exec \
  -n exercises \
  ping-pong-postgres-0 \
  -- psql \
    -U pingpong \
    -d pingpong \
    -c 'SELECT * FROM ping_pong_counter;'
```

## Deploy to GKE

Ping-pong is deployed together with Log output through the Gateway and
HTTPRoute defined in `log-output/manifests/gateway.yaml` and
`log-output/manifests/httproute.yaml`. The external `/pingpong` path is
rewritten to `/` before the request is forwarded to Ping-pong.

See the [Log output deployment instructions](../log-output/README.md#deploy-to-gke)
for the combined GKE deployment and functional tests.
