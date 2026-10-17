# Tomcat observability

Two independent local deployments of Tomcat 10.1 / JDK 17, Prometheus,
Alertmanager, Grafana, Loki, Tempo and OpenTelemetry:

| Deployment | Guide | Runtime |
| --- | --- | --- |
| Docker Compose | [dockercompose/README.md](dockercompose/README.md) | Docker Engine + Compose v2 |
| Kubernetes | [kubernetes/README.md](kubernetes/README.md) | Local k3s, or k3d running k3s in Docker |

The previous project is now entirely under `dockercompose/`. Run existing
Compose commands from that directory. The Compose project name is unchanged,
so existing named volumes are retained when using the same Docker daemon.
Move any local `.env` and secret files with the installation; do not recreate
credentials to recover access to an existing Grafana database.

The Dockerfile, telemetry configuration and Grafana dashboard in `dockercompose/`
are the canonical sources for both deployments. After changing them, run:

```bash
python tomcat-observability/kubernetes/render.py
python tomcat-observability/kubernetes/render.py --check
```

Commit the generated `kubernetes/resources.json` too. Rendering uses only the
Python standard library. Kubernetes JSON resources are directly accepted by kubectl.

GitHub Actions runs configuration and shell checks, a Compose build and smoke
test, security scans, and a k3s deployment with telemetry checks. See
[the workflow](../.github/workflows/tomcat-observability.yml).
It runs on relevant pushes, pull requests and manual dispatch. The cluster is
ephemeral on the runner; deploying to a workstation's local k3s remains a local action.
