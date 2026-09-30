# Todo app

Serves the Todo application HTML, caches the Lorem Picsum image on a persistent volume and communicates with `todo-backend-svc` over HTTP.

The form accepts todos of at most 140 characters. Todo items are fetched from the backend and rendered server-side. Incomplete todos can be marked done from the UI. The Break button marks the backend unhealthy, displays a System Failure page and lets the liveness probe restart the backend.

The application has separate `staging` and `production` namespaces.

Runtime URLs, ports, paths and timeout values are passed to the Pod as environment variables in the Deployment.

## Deploy with GitOps

GitHub Actions publishes the Todo app, backend and broadcaster to GHCR. Each commit to `main` updates the staging overlay; each tag builds that revision and updates the `production-release` branch. Argo CD synchronizes staging from `main` and production from `production-release`. The workflow can also be run manually for either environment.

Manifests and overlays are maintained in [KubernetesProjectConfig](https://github.com/antief/KubernetesProjectConfig). Clone that repository and follow its setup instructions. The source workflow requires a `CONFIG_REPO_TOKEN` repository secret with write access to the configuration repository.

Both environments use separate dynamically provisioned volumes and NATS subjects. Staging broadcasts are logged locally and its database is not backed up. Production forwards broadcasts to the webhook and backs up PostgreSQL daily.

```bash
kubectl get applications -n argocd
kubectl get deployments,pods,services,ingress,pvc -n staging
kubectl get deployments,pods,services,ingress,pvc,cronjobs -n production
```

Open <http://staging.todo.local:8081/> or <http://production.todo.local:8081/> with both names resolving to `127.0.0.1`.
