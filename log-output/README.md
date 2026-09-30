# Log output

The application runs as two containers in a single Kubernetes Pod.

- `log-output-writer` generates one UUID on startup and writes it with a UTC timestamp every five seconds.
- `log-output-reader` exposes the latest log line through HTTP.
- The containers share the log file through an `emptyDir` volume.
- The reader fetches the Ping-pong counter from `ping-pong-svc`.
- `GET /healthz` succeeds when Ping-pong is available.
- A ConfigMap provides the `MESSAGE` environment variable and the mounted `information.txt` file.

The application is deployed to the `exercises` namespace.

## GitOps

The Kubernetes resources are managed with Kustomize and Argo CD.

Changes pushed to `main` trigger the GitHub Actions workflow, which:

1. builds the Log output image,
2. pushes it to GitHub Container Registry,
3. updates the image tag in `kustomization.yaml` to the commit SHA,
4. commits the updated desired state back to the repository.

Argo CD watches the `log-output` directory and automatically synchronizes the desired state to the cluster.

## Validate

```bash
kubectl get application log-output -n argocd

kubectl get pods \
  -n exercises \
  -l app=log-output

kubectl rollout status \
  deployment/log-output-dep \
  -n exercises
```

Test the application:

```bash
kubectl exec -i \
  -n exercises \
  deployment/log-output-dep \
  -c log-output-reader \
  -- python -c '
from urllib.request import urlopen

for path in ["/", "/healthz"]:
    with urlopen("http://localhost:8000" + path, timeout=5) as response:
        print(path, response.status)
        print(response.read().decode(), end="")
'
```
