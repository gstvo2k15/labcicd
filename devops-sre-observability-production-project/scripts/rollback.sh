#!/usr/bin/env bash
set -euo pipefail
NAMESPACE="${1:-order-sre}"
DEPLOYMENT="${2:-order-service}"
kubectl rollout history deployment/"$DEPLOYMENT" -n "$NAMESPACE"
kubectl rollout undo deployment/"$DEPLOYMENT" -n "$NAMESPACE"
kubectl rollout status deployment/"$DEPLOYMENT" -n "$NAMESPACE"
