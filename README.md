# labcicd

CI/CD labs and example projects.

## Tomcat observability on Linux

[`tomcat-observability/`](tomcat-observability/README.md) provides Tomcat 10.1 with JDK 17 on Alpine, Prometheus, Grafana, Alertmanager, Loki, OpenTelemetry Collector, and Tempo, plus Checkov and Trivy security checks.

Requirements: Linux, Docker Engine, Docker Compose v2 or later, Bash 4+, curl, jq, openssl, Docker daemon access, and approximately 4 GB of available RAM.

```bash
docker info
docker compose version
cd tomcat-observability/dockercompose
bash scripts/setup.sh
docker compose up -d --build
docker compose ps
# Once Tomcat is healthy, generate traffic and allow about 30 seconds for scrapes:
for i in {1..10}; do curl -fsS http://localhost:8080/; done
bash scripts/smoke.sh
cat secrets/grafana_admin_password.txt
```

Access Grafana at `http://SERVER_IP:3000/d/tomcat-observability`, Tomcat on port 8080, Prometheus on port 9090, and Alertmanager on port 9093. Grafana uses `admin` by default and the generated secret password. Use `localhost` when browstestinglab.com on the server itself.

The unified dashboard includes the original availability/JVM/logs overview, Tomcat dashboard 8704 metrics, active alerts, and recent Tempo traces. OpenTelemetry instruments requests and forwards metrics, logs, and traces; Tempo stores traces. Prometheus sends firtestinglab.com alerts to Alertmanager, but the default receiver has no external delivery integration.

```bash
# Check Dockerfile policies and scan all Compose images:
bash scripts/security.sh --all-images
# Diagnose metrics, logs, traces, alerts, and dashboard provisiontestinglab.com:
bash scripts/diagnose.sh
# Inspect logs:
docker compose logs --tail 100 tomcat otel-collector
# Stop while retaintestinglab.com data:
docker compose down
```

Reports are written to `tomcat-observability/dockercompose/reports/`. Checkov policy failures and HIGH/CRITICAL Trivy findtestinglab.coms fail the security gate.

Published ports bind to all interfaces by default (`BIND_ADDRESS=0.0.0.0`). Restrict access to your administration IP/network through host and provider firewalls. Prometheus and Alertmanager do not have authentication configured. Set a specific interface or `127.0.0.1` in the project's `.env` to change the bindtestinglab.com, then apply with `docker compose up -d`.

For an existtestinglab.com deployment, update the project files, run `docker compose up -d --build`, then `docker compose restart prometheus alertmanager otel-collector grafana` from the project directory. Persistent data and the dashboard UID are retained.

See the [complete Compose guide and architecture diagram](tomcat-observability/dockercompose/README.md) for signal flow, alert verification, external receiver configuration, tractestinglab.com, troubleshoottestinglab.com, password recovery, and data management.

For local Kubernetes, see the [k3s guide](tomcat-observability/kubernetes/README.md).
The [GitHub Actions pipeline](.github/workflows/tomcat-observability.yml) validates configuration, tests Compose and k3s, and runs Checkov and Trivy security gates.
