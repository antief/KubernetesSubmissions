# Log output

The application runs as two containers in a single Kubernetes Pod.

- `log-output-writer` generates one UUID on startup and writes it with a UTC timestamp every five seconds.
- `log-output-reader` exposes the latest log line through HTTP.
- The containers share the log file through an `emptyDir` volume.
- The reader fetches the Ping-pong counter over HTTP from `ping-pong-svc`.

The application is deployed to the `exercises` namespace.

## Run locally

Create a virtual environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdir -p /tmp/log-output
```

Start the writer:

```bash
OUTPUT_FILE=/tmp/log-output/output.txt python writer.py
```

Start Ping-pong on port 8001, then start the reader:

```bash
OUTPUT_FILE=/tmp/log-output/output.txt \
PING_PONG_URL=http://localhost:8001/pings \
PORT=8000 \
python app.py
```

## Build

```bash
docker build -t log-output:2.1 .
```

## Deploy to k3d

From the repository root:

```bash
kubectl apply -f namespaces/exercises.yaml
k3d image import log-output:2.1 -c k3s-default
kubectl apply -f log-output/manifests/
```

Inspect the resources:

```bash
kubectl get pods,services -n exercises
```
