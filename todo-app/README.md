# Todo app

Serves the Todo application HTML, caches the Lorem Picsum image on a persistent volume and communicates with `todo-backend-svc` over HTTP.

The form accepts todos of at most 140 characters. Todo items are fetched from the backend and rendered server-side. Incomplete todos can be marked done from the UI. The Break button marks the backend unhealthy, displays a System Failure page and lets the liveness probe restart the backend.

The application is deployed to the `project` namespace.

Runtime URLs, ports, paths and timeout values are passed to the Pod as environment variables in the Deployment.

## Deploy with GitOps

GitHub Actions builds and publishes the Todo app, backend and broadcaster to GHCR on changes to `main`. It updates the images in the root `kustomization.yaml`; Argo CD synchronizes the desired state to the `project` namespace.

Prepare the namespace, local image volume, NATS and secrets as described in the backend and broadcaster READMEs. Then register the application:

```bash
kubectl apply -f namespaces/project.yaml

docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/todo-image
kubectl apply -f storage/todo-image-persistentvolume.yaml
kubectl apply -n argocd -f argocd/project-application.yaml
```

Check synchronization and workloads:

```bash
kubectl get application project -n argocd
kubectl get deployments,pods,services,ingress,pvc -n project
```

Open <http://localhost:8081/>.
