# Ping-pong

Provides three HTTP endpoints:

- `GET /` returns the current counter and increments it.
- `GET /pings` returns the current counter without modifying it.
- `GET /healthz` succeeds when the database connection works.

The counter is stored in PostgreSQL.

PostgreSQL runs as a single-replica StatefulSet using the cluster's default StorageClass. The application is managed by an Argo Rollout in the `exercises` namespace. Canary updates use the `ping-pong-cpu` AnalysisTemplate to check the five-minute CPU usage rate sum for containers in the namespace through Prometheus. The normal success threshold is `0.1`.

## Build

```bash
docker build \
  -t europe-north1-docker.pkg.dev/dwk-gke-antti-6c49/dwk-images/ping-pong:4.1 \
  .
```

## Deploy to k3d

Argo Rollouts and Prometheus must already be installed in the cluster.

From the repository root:

```bash
kubectl apply -f namespaces/exercises.yaml

docker build \
  -t europe-north1-docker.pkg.dev/dwk-gke-antti-6c49/dwk-images/ping-pong:4.1 \
  ./ping-pong

docker pull docker.io/library/postgres:18.0

k3d image import \
  europe-north1-docker.pkg.dev/dwk-gke-antti-6c49/dwk-images/ping-pong:4.1 \
  docker.io/library/postgres:18.0 \
  -c k3s-default

kubectl apply \
  -f ping-pong/manifests/postgres.yaml

kubectl rollout status \
  statefulset/ping-pong-postgres \
  -n exercises

kubectl apply \
  -f ping-pong/manifests/analysistemplate.yaml \
  -f ping-pong/manifests/deployment.yaml \
  -f ping-pong/manifests/service.yaml

kubectl wait \
  --for=condition=Available \
  rollout/ping-pong-dep \
  -n exercises \
  --timeout=2m
```

Inspect the resources:

```bash
kubectl get rollout,analysistemplate,statefulset,pods,services,pvc \
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

The cluster must have Argo Rollouts and Prometheus installed. Prometheus is
available to the AnalysisTemplate through
`prom-prometheus-server.monitoring.svc.cluster.local`.

From the repository root:

    kubectl apply \
      -f ping-pong/manifests/postgres.yaml \
      -f ping-pong/manifests/analysistemplate.yaml \
      -f ping-pong/manifests/deployment.yaml \
      -f ping-pong/manifests/service.yaml

    kubectl wait \
      --for=condition=Available \
      rollout/ping-pong-dep \
      -n exercises \
      --timeout=2m

Ping-pong remains exposed at `/pingpong` through the Gateway and HTTPRoute
defined under `log-output/manifests/`.
