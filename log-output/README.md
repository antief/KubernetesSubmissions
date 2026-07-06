# Log output

The application runs as two containers in a single Kubernetes Pod.

- `log-output-writer` generates one UUID on startup and appends it with a UTC timestamp to a shared file every five seconds.
- `log-output-reader` reads the shared file and exposes its contents through an HTTP GET endpoint.

The containers share the file using an `emptyDir` volume.

## Run locally

Create a virtual environment and install the HTTP server dependencies:

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

Start the reader in another terminal:

```bash
source .venv/bin/activate
OUTPUT_FILE=/tmp/log-output/output.txt PORT=8000 python app.py
```

Open <http://localhost:8000>.

## Build

```bash
docker build -t log-output:1.10 .
```

## Deploy to k3d

```bash
k3d image import log-output:1.10 -c k3s-default
kubectl apply -f manifests/
```

The application is available through the course ingress at <http://localhost:8081/>.
