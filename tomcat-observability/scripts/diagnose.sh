#!/usr/bin/env bash
# Solo lectura: no cambia credenciales, contenedores ni datos.
set -uo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
command -v curl >/dev/null || { echo 'Instala curl.' >&2; exit 1; }
command -v jq >/dev/null || { echo 'Instala jq.' >&2; exit 1; }
failed=0

echo '=== Estado de contenedores ==='
docker compose ps || failed=1

echo '=== Paneles montados en Grafana (debe aparecer Logs de Tomcat) ==='
if dashboard="$(docker compose exec -T grafana cat /var/lib/grafana/dashboards/tomcat.json)"; then
  jq -r '.uid, (.panels[] | "\(.id): \(.title) [\(.type)]")' <<< "$dashboard" || failed=1
  jq -e 'any(.panels[]; .type == "logs" and .datasource.uid == "loki")' <<< "$dashboard" >/dev/null || failed=1
else
  failed=1
fi

echo '=== Targets cargados por Prometheus ==='
if targets="$(curl -fsS --max-time 10 http://localhost:9090/api/v1/targets)"; then
  jq -r '.data.activeTargets[] | "\(.labels.job): \(.health) \(.scrapeUrl) \(.lastError)"' <<< "$targets" || failed=1
  if ! jq -e 'any(.data.activeTargets[]; .labels.job == "tomcat-jmx" and .health == "up")' <<< "$targets" >/dev/null; then
    echo 'ERROR: falta tomcat-jmx o su scrape falla.' >&2
    failed=1
  fi
else
  failed=1
fi

echo '=== Familias JMX y OpenTelemetry presentes ==='
if metrics="$(curl -fsS --max-time 10 --get \
  --data-urlencode 'query=count by (__name__,job) ({__name__=~"tomcat_.*|jvm_memory_used_bytes"})' \
  http://localhost:9090/api/v1/query)"; then
  jq '.data.result[] | {metric: .metric, series: .value[1]}' <<< "$metrics" || failed=1
else
  failed=1
fi

echo '=== Respuesta directa de JMX Exporter desde la red Compose ==='
if jmx="$(docker compose exec -T tomcat wget -q -T 10 -O - http://127.0.0.1:9404/metrics)"; then
  printf '%s\n' "$jmx" | awk '/^tomcat_|^jmx_scrape_error/ {print; n++; if(n>=30) exit}'
  if [[ "$jmx" != *'tomcat_requestcount_total'* ]]; then
    echo 'ERROR: el exporter no devuelve tomcat_requestcount_total.' >&2
    failed=1
  fi
else
  failed=1
fi

echo '=== Logs recibidos por Loki en la ultima hora ==='
# Tomcat incluye wget; Loki no necesita publicar su puerto en el host.
if logs="$(docker compose exec -T tomcat wget -q -T 10 -O - \
  'http://loki:3100/loki/api/v1/query_range?query=%7Bservice_name%3D%22tomcat%22%7D&since=1h&limit=3')"; then
  jq '{status, streams: (.data.result | length), sample: .data.result}' <<< "$logs" || failed=1
  if ! jq -e '.status == "success" and (.data.result | length > 0)' <<< "$logs" >/dev/null; then
    echo 'ERROR: Loki no devuelve logs de Tomcat en la ultima hora.' >&2
    failed=1
  fi
else
  failed=1
fi

echo '=== Logs recientes de los componentes ==='
docker compose logs --since 5m --tail 40 tomcat otel-collector prometheus loki grafana || failed=1
exit "$failed"
