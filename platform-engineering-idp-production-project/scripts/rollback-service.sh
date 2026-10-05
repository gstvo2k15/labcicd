#!/usr/bin/env bash
set -euo pipefail
NS="${1:?namespace}"; DEPLOY="${2:?deployment}"
kubectl rollout undo deployment/$DEPLOY -n $NS
kubectl rollout status deployment/$DEPLOY -n $NS
