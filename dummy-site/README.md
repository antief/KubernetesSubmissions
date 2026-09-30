# DummySite

A namespaced `DummySite` resource declares `spec.website_url`. The Python controller watches these resources and creates a Deployment and Service. An init container downloads the page; nginx serves the saved HTML. Updating the URL triggers a rollout. Owner references remove the generated resources when the DummySite is deleted.

## Deploy to k3d

From the repository root:

```bash
docker build -t dummy-site-controller:5.1 ./dummy-site
k3d image import dummy-site-controller:5.1 -c k3s-default
kubectl apply -f namespaces/exercises.yaml
kubectl apply -f dummy-site/manifests/crd.yaml
kubectl wait --for=condition=Established crd/dummysites.stable.dwk
kubectl apply -f dummy-site/manifests/rbac.yaml
kubectl apply -f dummy-site/manifests/deployment.yaml
kubectl apply -n exercises -f dummy-site/manifests/example.yaml
```

Find the generated Service and forward its port:

```bash
kubectl get services -n exercises -l app.kubernetes.io/managed-by=dummy-site-controller
kubectl port-forward -n exercises service/<generated-service-name> 8082:80
```

Open <http://localhost:8082/> to see the copy of Example Domain. Only the HTML is copied; external styles and other assets are not mirrored.
