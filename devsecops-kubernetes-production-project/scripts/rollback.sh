#!/usr/bin/env bash
set -euo pipefail
kubectl -n order-management rollout undo deployment/api-gateway
kubectl -n order-management rollout status deployment/api-gateway
