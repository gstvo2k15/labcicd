#!/usr/bin/env bash
# Read only: does not change credentials, containers, or data.
set -uo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
command -v curl >/dev/null || { echo 'Install curl.' >&2; exit 1; }
command -v jq >/dev/null || { echo 'Install jq.' >&2; exit 1; }
failed=0

echo '=== Container status ==='
docker compose ps || failed=1

echo '=== Panels mounted in Grafana (Tomcat logs must appear) ==='
if dashboard="$(docker compose exec -T grafana cat /var/lib/grafana/dashboards/tomcat.json)"; then
  jq -r '.uid, (.panels[] | "\(.id): \(.title) [\(.type)]")' <<< "$dashboard" || failed=1
  jq -e 'any(.panels[]; .type == "logs" and .datasource.uid == "loki")' <<< "$dashboard" >/dev/null || failed=1
else
  failed=1
fi

echo '=== Targets loaded by Prometheus ==='
if targets="$(curl -fsS --max-time 10 http://localhost:9090/api/v1/targets)"; then
  jq -r '.data.activeTargets[] | "\(.labels.job): \(.health) \(.scrapeUrl) \(.lastError)"' <<< "$targets" || failed=1
  if ! jq -e 'any(.data.activeTargets[]; .labels.job == "tomcat-jmx" and .health == "up")' <<< "$targets" >/dev/null; then
    echo 'ERROR: tomcat-jmx is missing or its scrape is failing.' >&2
    failed=1
  fi
else
  failed=1
fi

echo '=== Available JMX and OpenTelemetry metric families ==='
if metrics="$(curl -fsS --max-time 10 --get \
  --data-urlencode 'query=count by (__name__,job) ({__name__=~"tomcat_.*|jvm_memory_used_bytes"})' \
  http://localhost:9090/api/v1/query)"; then
  jq '.data.result[] | {metric: .metric, series: .value[1]}' <<< "$metrics" || failed=1
else
  failed=1
fi

echo '=== Direct JMX Exporter response inside the Compose network ==='
if jmx="$(docker compose exec -T tomcat wget -q -T 10 -O - http://127.0.0.1:9404/metrics)"; then
  printf '%s\n' "$jmx" | awk '/^tomcat_|^jmx_scrape_error/ {print; n++; if(n>=30) exit}'
  if [[ "$jmx" != *'tomcat_requestcount_total'* ]]; then
    echo 'ERROR: the exporter does not return tomcat_requestcount_total.' >&2
    failed=1
  fi
else
  failed=1
fi

echo '=== Logs received by Loki in the last hour ==='
# Tomcat includes wget; Loki does not need a published host port.
if logs="$(docker compose exec -T tomcat wget -q -T 10 -O - \
  'http://loki:3100/loki/api/v1/query_range?query=%7Bservice_name%3D%22tomcat%22%7D&since=1h&limit=3')"; then
  jq '{status, streams: (.data.result | length), sample: .data.result}' <<< "$logs" || failed=1
  if ! jq -e '.status == "success" and (.data.result | length > 0)' <<< "$logs" >/dev/null; then
    echo 'ERROR: Loki returned no Tomcat logs for the last hour.' >&2
    failed=1
  fi
else
  failed=1
fi

echo '=== Recent Tomcat traces stored in Tempo ==='
if traces="$(docker compose exec -T tomcat wget -q -T 10 -O - \
  'http://tempo:3200/api/search?q=%7B%20resource.service.name%20%3D%20%22tomcat%22%20%7D&limit=3')"; then
  jq '{traceCount: (.traces // [] | length), traces, metrics}' <<< "$traces" || failed=1
  if ! jq -e '(.traces // [] | length) > 0' <<< "$traces" >/dev/null; then
    echo 'ERROR: no Tomcat traces found. Generate HTTP traffic and check the agent/Collector trace pipeline.' >&2
    failed=1
  fi
else
  failed=1
fi

echo '=== Prometheus alert rules and states ==='
if alerts="$(curl -fsS --max-time 10 http://localhost:9090/api/v1/rules?type=alert)"; then
  jq '.data.groups[] | {name, rules: [.rules[] | {name, state, health, lastError}]}' <<< "$alerts" || failed=1
else
  failed=1
fi

echo '=== Alerts received by Alertmanager (an empty list is healthy when no rules are firing) ==='
if alerts="$(curl -fsS --max-time 10 http://localhost:9093/api/v2/alerts)"; then
  jq . <<< "$alerts" || failed=1
else
  failed=1
fi

echo '=== Recent component logs ==='
docker compose logs --since 5m --tail 40 tomcat otel-collector prometheus loki grafana || failed=1
exit "$failed"
