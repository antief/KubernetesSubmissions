# Log output

Generates one UUID on startup, prints it with a UTC timestamp every five seconds, and exposes the current status over HTTP.

## Run

```bash
PORT=8000 python app.py
```

## Build

```bash
docker build -t log-output:1.7 .
```
