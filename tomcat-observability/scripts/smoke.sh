#!/usr/bin/env bash
set -Eeuo pipefail

command -v curl >/dev/null || { echo 'Instala curl.' >&2; exit 1; }
command -v jq >/dev/null || { echo 'Instala jq.' >&2; exit 1; }

for (( i=0; i<10; i++ )); do
  response="$(curl --fail --silent --show-error --max-time 10 http://localhost:8080/)"
  [[ "$response" == *'Tomcat 10'* ]] || { echo 'Respuesta inesperada de Tomcat.' >&2; exit 1; }
done

curl --fail --silent --show-error --max-time 10 http://localhost:9090/-/ready >/dev/null
targets="$(curl --fail --silent --show-error --max-time 10 http://localhost:9090/api/v1/targets)"

if ! jq -e '.status == "success" and (.data.activeTargets | length > 0) and all(.data.activeTargets[]; .health == "up")' <<< "$targets" >/dev/null; then
  echo 'Targets de Prometheus no disponibles:' >&2
  jq '.data.activeTargets[] | {job: .labels.job, health, lastError}' <<< "$targets" >&2
  exit 1
fi

# Un scrape UP no garantiza que las reglas exporten los MBeans del dashboard.
metrics="$(curl --fail --silent --show-error --max-time 10 --get \
  --data-urlencode 'query=count by (__name__) ({job="tomcat-jmx",__name__=~"tomcat_serverinfo|tomcat_requestcount_total|tomcat_threadpool_maxthreads|tomcat_session_activesessions|tomcat_servlet_requestcount_total"})' \
  http://localhost:9090/api/v1/query)"
if ! jq -e '.status == "success" and (.data.result | length == 5)' <<< "$metrics" >/dev/null; then
  echo 'Faltan familias de metricas JMX. Espera un scrape y revisa Tomcat y config/jmx-exporter.yaml.' >&2
  jq '.data.result' <<< "$metrics" >&2
  exit 1
fi

echo 'HTTP, targets y familias JMX correctos. Verifica logs y trazas en Grafana segun README.'
