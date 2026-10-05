#!/usr/bin/env bash
set -euo pipefail
REGISTRY=${REGISTRY:?Set REGISTRY}; TAG=${TAG:-1.0.0}
for s in api-gateway user-service restaurant-service order-service payment-service notification-service frontend; do docker push "$REGISTRY/food-$s:$TAG"; done
