# Log output

The application runs as two containers in a single Kubernetes Pod.

- `log-output-writer` generates one UUID on startup and appends it with a UTC timestamp to a shared file every five seconds.
- `log-output-reader` reads the latest line and exposes it through an HTTP GET endpoint.
- The reader also displays the Ping-pong request counter stored in the shared persistent volume.

The Log output and Ping-pong Pods mount the same PersistentVolumeClaim.

## Run locally

Create a virtual environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdir -p /tmp/log-output
printf '0\n' > /tmp/log-output/ping-pong.txt
```

Start the writer:

```bash
OUTPUT_FILE=/tmp/log-output/output.txt python writer.py
```

Start the reader in another terminal:

```bash
source .venv/bin/activate
OUTPUT_FILE=/tmp/log-output/output.txt \
PING_PONG_FILE=/tmp/log-output/ping-pong.txt \
PORT=8000 \
python app.py
```

Open <http://localhost:8000>.

## Build

```bash
docker build -t log-output:1.11 .
```

## Deploy to k3d

From the repository root:

```bash
k3d image import log-output:1.11 -c k3s-default
kubectl apply -f storage/
kubectl apply -f log-output/manifests/
```

The application is available through the course ingress at <http://localhost:8081/>.
