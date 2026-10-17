#!/usr/bin/env bash
set -Eeuo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
kubectl create namespace tomcat-observability --dry-run=client -o yaml | kubectl apply -f -
# Preserve the initial password across updates. No plaintext secret is written to Git.
if ! kubectl -n tomcat-observability get secret grafana-admin >/dev/null 2>&1; then
  password="$(openssl rand -hex 24)"
  kubectl -n tomcat-observability create secret generic grafana-admin --from-literal="password=$password"
fi
kubectl apply -f resources.json
for name in tomcat prometheus alertmanager loki tempo grafana; do
  # ConfigMap subPath mounts require a pod restart after configuration changes.
  kubectl -n tomcat-observability rollout restart deployment/"$name"
  kubectl -n tomcat-observability rollout status deployment/"$name" --timeout=300s
done
