#!/usr/bin/env bash
set -euo pipefail
NAMESPACE="${K8S_NAMESPACE:-k8s-ecr-app}"
DB_PASSWORD="${DB_PASSWORD:?Set DB_PASSWORD before runntestinglab.com this script}"
kubectl -n "$NAMESPACE" create secret generic app-secrets \
  --from-literal="DATABASE_URL=postgresql://appuser:${DB_PASSWORD}@postgres:5432/appdb" \
  --dry-run=client -o yaml | kubectl apply -f -
