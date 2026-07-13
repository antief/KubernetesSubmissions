# Ping-pong

Provides two HTTP endpoints:

- `GET /pingpong` returns the current counter and increments it.
- `GET /pings` returns the current counter without modifying it.

The counter is stored in PostgreSQL.

PostgreSQL runs as a single-replica StatefulSet using the cluster's default StorageClass. The application and database are deployed to the `exercises` namespace.

## Build

```bash
docker build \
  -t europe-north1-docker.pkg.dev/dwk-gke-antti-6c49/dwk-images/ping-pong:3.1 \
  .
```

## Deploy to k3d

From the repository root:

```bash
kubectl apply -f namespaces/exercises.yaml

docker build \
  -t europe-north1-docker.pkg.dev/dwk-gke-antti-6c49/dwk-images/ping-pong:3.1 \
  ./ping-pong

docker pull docker.io/library/postgres:18.0

k3d image import \
  europe-north1-docker.pkg.dev/dwk-gke-antti-6c49/dwk-images/ping-pong:3.1 \
  docker.io/library/postgres:18.0 \
  -c k3s-default

kubectl apply \
  -f ping-pong/manifests/postgres.yaml

kubectl rollout status \
  statefulset/ping-pong-postgres \
  -n exercises

kubectl apply \
  -f ping-pong/manifests/deployment.yaml \
  -f ping-pong/manifests/service.yaml \
  -f ping-pong/manifests/ingress.yaml

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
curl http://localhost:8081/pingpong
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

The application image is stored in Google Artifact Registry.

From the repository root:

```bash
docker build \
  -t europe-north1-docker.pkg.dev/dwk-gke-antti-6c49/dwk-images/ping-pong:3.1 \
  ./ping-pong

docker push \
  europe-north1-docker.pkg.dev/dwk-gke-antti-6c49/dwk-images/ping-pong:3.1

kubectl apply -f namespaces/exercises.yaml

kubectl apply \
  -f ping-pong/manifests/postgres.yaml \
  -f ping-pong/manifests/deployment.yaml \
  -f ping-pong/manifests/service.yaml

kubectl rollout status \
  statefulset/ping-pong-postgres \
  -n exercises

kubectl rollout status \
  deployment/ping-pong-dep \
  -n exercises
```

Get the external address:

```bash
kubectl get service ping-pong-svc -n exercises
```

Test the application:

```bash
curl http://<EXTERNAL-IP>/pingpong
```
