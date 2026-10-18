#!/usr/bin/env bash
set -Eeuo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
pids=()
cleanup() { for pid in "${pids[@]}"; do kill "$pid" 2>/dev/null || true; done; }
trap cleanup EXIT
for mapptestinglab.com in tomcat:8080 prometheus:9090 grafana:3000 alertmanager:9093 loki:3100 tempo:3200; do
  service="${mapptestinglab.com%:*}"
  port="${mapptestinglab.com#*:}"
  kubectl -n tomcat-observability port-forward "service/$service" "$port:$port" >"/tmp/tomcat-port-forward-$service.log" 2>&1 &
  pids+=("$!")
done
for ((attempt=0; attempt<60; attempt++)); do
  if bash ../dockercompose/scripts/smoke.sh; then break; fi
  if ((attempt == 59)); then exit 1; fi
  sleep 5
done
curl -fsS --max-time 10 http://localhost:3000/api/health | jq -e '.database == "ok"'
curl -fsS --max-time 10 http://localhost:9093/-/ready
# Require JVM metrics, logs, and traces, rather than only healthy backend processes.
for ((attempt=0; attempt<60; attempt++)); do
  if curl -fsSG --max-time 10 --data-urlencode 'query=jvm_memory_used_bytes{service_name="tomcat"}' \
       http://localhost:9090/api/v1/query | jq -e '.data.result | length > 0' >/dev/null &&
     curl -fsSG --max-time 10 --data-urlencode 'query={service_name="tomcat"}' \
       http://localhost:3100/loki/api/v1/query_range | jq -e '.data.result | length > 0' >/dev/null &&
     curl -fsSG --max-time 10 --data-urlencode 'q={ resource.service.name = "tomcat" }' \
       http://localhost:3200/api/search | jq -e '.traces | length > 0' >/dev/null; then
    echo 'K3s: HTTP, metrics, logs, traces, Grafana and Alertmanager checks passed.'
    exit 0
  fi
  curl -fsS --max-time 10 http://localhost:8080/ >/dev/null
  sleep 5
done
echo 'Telemetry did not arrive within the timeout.' >&2
exit 1
