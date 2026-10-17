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

echo 'HTTP y targets correctos. Tras 30 segundos, verificar métricas, logs y trazas en Grafana según README.'
