# Ping-pong

Provides three HTTP endpoints:

- `GET /` returns the current counter and increments it.
- `GET /pings` returns the current counter without modifying it.
- `GET /healthz` succeeds when the database connection works.

The application runs as a Knative Service in the `exercises` namespace. Knative supplies `PORT`, creates revisions, and scales the application to zero when idle. PostgreSQL retains the counter in its existing single-replica StatefulSet and persistent volume.

## Deploy

Knative Serving and Kourier must already be installed. For a new installation, create the database from `manifests/postgres.yaml`:

```bash
kubectl apply -f namespaces/exercises.yaml
kubectl create -f ping-pong/manifests/postgres.yaml
kubectl rollout status statefulset/ping-pong-postgres -n exercises
```

The Log output GitOps workflow builds and publishes the Ping-pong image alongside Log output and Greeter. Its Kustomization includes the Knative Service, and Argo CD synchronizes it. Log output calls `http://ping-pong.exercises.svc.cluster.local/pings`; its readiness probe does not call Ping-pong, allowing idle scale-to-zero.

## Validate

```bash
kubectl wait --for=condition=Ready ksvc/ping-pong -n exercises --timeout=2m
kubectl get ksvc,revision,pods -n exercises -l serving.knative.dev/service=ping-pong
kubectl get ksvc ping-pong -n exercises
```

The Log output Istio gateway rewrites `/pingpong` to `/` and sets the fully qualified Knative service hostname:

```bash
kubectl port-forward -n exercises service/log-output-gateway-istio 8082:80
```

In another terminal:

```bash
curl --fail --show-error --max-time 30 http://localhost:8082/pingpong
curl --fail --show-error --max-time 30 http://localhost:8082/
```

After requests stop, the revision Deployment reaches zero replicas. A new request starts it again, while the database counter persists.

Inspect the stored counter:

```bash
kubectl exec -n exercises ping-pong-postgres-0 -- \
  psql -U pingpong -d pingpong -c 'SELECT * FROM ping_pong_counter;'
```
