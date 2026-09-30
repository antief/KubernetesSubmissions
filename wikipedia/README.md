# Wikipedia

nginx serves HTML from a shared `emptyDir`. The init container downloads the Kubernetes Wikipedia page before nginx starts. A sidecar waits a random 300–900 seconds, then follows `Special:Random` and replaces the served page. Downloads replace the file atomically; failures leave the previous page available.

```bash
kubectl apply -n exercises -f wikipedia/manifests
kubectl rollout status -n exercises deployment/wikipedia
kubectl port-forward -n exercises service/wikipedia 8084:80
```

Open <http://localhost:8084/>. Only the page HTML is stored; external assets are not mirrored.
