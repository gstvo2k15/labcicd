#!/usr/bin/env bash
set -euo pipefail
kubectl apply -f kubernetes/namespaces.yaml
kubectl apply -f kubernetes/resourcequotas.yaml
kubectl apply -f kubernetes/limitranges.yaml
kubectl apply -f kubernetes/rbac.yaml
kubectl apply -f kubernetes/networkpolicies.yaml
