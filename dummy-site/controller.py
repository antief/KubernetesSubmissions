import logging
import time

from kubernetes import client, config, watch
from kubernetes.client.exceptions import ApiException
from urllib3.exceptions import HTTPError


GROUP = "stable.dwk"
VERSION = "v1"
PLURAL = "dummysites"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("dummy-site-controller")


def resources(site):
    metadata = site["metadata"]
    name = f"dummy-{metadata['uid'][:12]}"
    labels = {"app": name, "app.kubernetes.io/managed-by": "dummy-site-controller"}
    owner = {
        "apiVersion": f"{GROUP}/{VERSION}",
        "kind": "DummySite",
        "name": metadata["name"],
        "uid": metadata["uid"],
        "controller": True,
    }
    resource_metadata = {"name": name, "labels": labels, "ownerReferences": [owner]}
    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": resource_metadata,
        "spec": {
            "replicas": 1,
            "selector": {"matchLabels": {"app": name}},
            "template": {
                "metadata": {"labels": labels},
                "spec": {
                    "securityContext": {"fsGroup": 101},
                    "volumes": [{"name": "site", "emptyDir": {}}],
                    "initContainers": [{
                        "name": "download",
                        "image": "curlimages/curl:8.11.1",
                        "env": [{"name": "WEBSITE_URL", "value": site["spec"]["website_url"]}],
                        "command": ["curl"],
                        "args": [
                            "--location", "--fail", "--show-error", "--silent",
                            "--retry", "3", "--connect-timeout", "10", "--max-time", "60",
                            "--output", "/site/index.html", "$(WEBSITE_URL)",
                        ],
                        "resources": {
                            "requests": {"cpu": "5m", "memory": "16Mi"},
                            "limits": {"cpu": "100m", "memory": "64Mi"},
                        },
                        "volumeMounts": [{"name": "site", "mountPath": "/site"}],
                    }],
                    "containers": [{
                        "name": "nginx",
                        "image": "nginx:1.31-alpine",
                        "ports": [{"name": "http", "containerPort": 80}],
                        "resources": {
                            "requests": {"cpu": "5m", "memory": "16Mi"},
                            "limits": {"cpu": "100m", "memory": "64Mi"},
                        },
                        "readinessProbe": {"httpGet": {"path": "/", "port": "http"}},
                        "volumeMounts": [{
                            "name": "site", "mountPath": "/usr/share/nginx/html", "readOnly": True,
                        }],
                    }],
                },
            },
        },
    }
    service = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": resource_metadata,
        "spec": {"selector": {"app": name}, "ports": [{"port": 80, "targetPort": "http"}]},
    }
    return deployment, service


def ensure_resource(site, body, read, create, patch):
    name = body["metadata"]["name"]
    namespace = site["metadata"]["namespace"]
    try:
        existing = read(name, namespace)
    except ApiException as error:
        if error.status != 404:
            raise
        create(namespace, body)
        return
    if not any(
        owner.uid == site["metadata"]["uid"]
        for owner in existing.metadata.owner_references or []
    ):
        raise RuntimeError(f"Resource {namespace}/{name} belongs to another owner")
    patch(name, namespace, body)


def reconcile(site, apps, core):
    if site["metadata"].get("deletionTimestamp"):
        return
    deployment, service = resources(site)
    ensure_resource(
        site, deployment, apps.read_namespaced_deployment,
        apps.create_namespaced_deployment, apps.patch_namespaced_deployment,
    )
    ensure_resource(
        site, service, core.read_namespaced_service,
        core.create_namespaced_service, core.patch_namespaced_service,
    )
    logger.info("Reconciled %s/%s", site["metadata"]["namespace"], site["metadata"]["name"])


def main():
    config.load_incluster_config()
    custom = client.CustomObjectsApi()
    apps = client.AppsV1Api()
    core = client.CoreV1Api()
    while True:
        try:
            sites = custom.list_cluster_custom_object(GROUP, VERSION, PLURAL)
            for site in sites["items"]:
                reconcile(site, apps, core)
            for event in watch.Watch().stream(
                custom.list_cluster_custom_object, GROUP, VERSION, PLURAL,
                resource_version=sites["metadata"]["resourceVersion"], timeout_seconds=30,
            ):
                if event["type"] in ("ADDED", "MODIFIED"):
                    reconcile(event["object"], apps, core)
        except (ApiException, HTTPError, OSError, RuntimeError):
            logger.exception("Reconciliation failed; retrying")
            time.sleep(3)


if __name__ == "__main__":
    main()
