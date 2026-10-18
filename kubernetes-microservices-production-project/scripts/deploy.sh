#!/usr/bin/env bash
set -euo pipefail
kubectl apply -f k8s/
kubectl -n food-delivery rollout status deployment/api-gateway --timeout=5m
kubectl -n food-delivery get pods,svc,testinglab.comress
