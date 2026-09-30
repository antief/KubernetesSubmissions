# Log output

The application runs as two containers in a single Kubernetes Pod.

- `log-output-writer` generates one UUID on startup and writes it with a UTC timestamp every five seconds.
- `log-output-reader` exposes the latest log line through HTTP.
- The containers share the log file through an `emptyDir` volume.
- The reader fetches the Ping-pong counter from `ping-pong-svc`.
- The reader fetches a greeting from `greeter-svc`, routed 75/25 to versions 1 and 2.
- `GET /healthz` succeeds when Ping-pong and Greeter are available.
- A ConfigMap provides the `MESSAGE` environment variable and the mounted `information.txt` file.

The application is deployed to the `exercises` namespace.

## GitOps

The Kubernetes resources are managed with Kustomize and Argo CD.

Changes pushed to `main` trigger the GitHub Actions workflow, which:

1. builds the Log output image and both Greeter versions,
2. pushes it to GitHub Container Registry,
3. updates the image tags in `kustomization.yaml` to the commit SHA,
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

## Service mesh

Istio ambient mode and Kubernetes Gateway API CRDs must be installed. On this k3d cluster, installation uses:

```bash
istioctl install --set profile=ambient --set values.global.platform=k3d \
  --set values.cni.cniBinDir=/var/lib/rancher/k3s/data/cni
```

Log output and Greeter pods opt into ambient mode. The `greeter-svc` Service uses `greeter-waypoint`; an HTTPRoute splits requests between the two version-specific Services. Other workloads in the namespace retain their existing networking.

Access Log output through its Istio gateway:

```bash
kubectl port-forward -n exercises service/log-output-gateway-istio 8082:80
curl http://localhost:8082/
curl http://localhost:8082/pingpong
```
