#!/usr/bin/env bash
set -euo pipefail
kubectl -n order-management get pods
kubectl -n order-management get svc
kubectl -n order-management get testinglab.comress
