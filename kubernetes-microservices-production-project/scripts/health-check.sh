#!/usr/bin/env bash
set -euo pipefail
kubectl -n food-delivery get pods
kubectl -n food-delivery get endpoints
kubectl -n food-delivery run curl --rm -it --restart=Never --image=curlimages/curl -- curl -sS http://api-gateway:8000/health
