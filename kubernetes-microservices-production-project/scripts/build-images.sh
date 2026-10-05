#!/usr/bin/env bash
set -euo pipefail
REGISTRY=${REGISTRY:?Set REGISTRY, e.g. myacr.azurecr.io}; TAG=${TAG:-1.0.0}
for s in api-gateway user-service restaurant-service order-service payment-service notification-service frontend; do docker build -t "$REGISTRY/food-$s:$TAG" "app/$s"; done
