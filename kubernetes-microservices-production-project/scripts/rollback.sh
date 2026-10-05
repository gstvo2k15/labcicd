#!/usr/bin/env bash
set -euo pipefail
SERVICE=${1:?service name required}
kubectl -n food-delivery rollout undo deployment/$SERVICE
kubectl -n food-delivery rollout status deployment/$SERVICE --timeout=5m
