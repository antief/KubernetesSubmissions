# Greeter

Returns a plain-text greeting on HTTP GET at port 8000. The image build argument `VERSION` selects the greeting version.

```bash
docker build --build-arg VERSION=1 -t greeter:1 ./greeter
docker build --build-arg VERSION=2 -t greeter:2 ./greeter
```

The Log output GitOps workflow publishes both versions. Deployments, Services, and the 75/25 waypoint route are in `log-output/manifests`.
