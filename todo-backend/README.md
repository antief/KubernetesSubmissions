# Todo backend

FastAPI backend for the Todo application. Todos are stored in PostgreSQL. Todo requests are logged, and todos longer than 140 characters are rejected.

A CronJob creates an hourly todo for a random Wikipedia article.

PostgreSQL runs as a single-replica StatefulSet. Database settings are provided through a ConfigMap and a SOPS-encrypted Secret.

## Build

```bash
docker build -t todo-backend:2.10 ./todo-backend
```

## Deploy

```bash
kubectl apply -f namespaces/project.yaml

docker pull postgres:18.0

k3d image import \
  todo-backend:2.10 \
  postgres:18.0 \
  -c k3s-default

export SOPS_AGE_KEY_FILE="$HOME/.config/sops/age/keys.txt"

sops --decrypt \
  todo-backend/manifests/secret.enc.yaml \
  | kubectl apply -f -

kubectl apply \
  -f todo-backend/manifests/configmap.yaml \
  -f todo-backend/manifests/postgres.yaml \
  -f todo-backend/manifests/deployment.yaml \
  -f todo-backend/manifests/service.yaml \
  -f todo-backend/manifests/cronjob.yaml
```

## Exercise 3.9: DBaaS vs DIY

### Database as a Service

**Pros**

- The database can be set up quickly because the server, storage and database installation are provided by the cloud provider.
- Routine maintenance, security patches and many version upgrades are handled by the provider.
- Automated backups and point-in-time recovery can usually be enabled with only a few configuration choices.
- High availability, monitoring and storage expansion can be added relatively easily.

**Cons**

- A managed database usually costs more than a small PostgreSQL instance running in an existing Kubernetes cluster.
- Backups, high availability and network traffic may increase the monthly cost further.
- Less control is available over the database server, supported versions and extensions.
- Greater dependency on the chosen cloud provider is introduced.

### Self-hosted PostgreSQL in Kubernetes

**Pros**

- Direct infrastructure costs can be lower because the existing Kubernetes nodes and storage can be used.
- Full control is retained over the PostgreSQL version, configuration and extensions.
- The setup can be moved more easily between different Kubernetes environments.
- The solution is suitable for a small course project where high availability is not required.

**Cons**

- More initial setup work is required because the StatefulSet, persistent storage, networking, credentials and health checks must be configured.
- Database updates, security patches, monitoring, storage capacity and failure recovery must be handled separately.
- Backups must be implemented, for example with `pg_dump`, a CronJob and external object storage.
- Backup retention, restoration and restore testing must also be planned and maintained.
- High availability is not provided by a single PostgreSQL Pod and persistent volume.

For this course project, self-hosted PostgreSQL is a reasonable and inexpensive choice. For a production service where availability and recovery are important, a managed database would reduce the amount of maintenance required.
