#!/usr/bin/env bash
set -euo pipefail
cp -n k8s/secret.example.yaml k8s/secret.local.yaml || true
echo 'Edit k8s/secret.local.yaml with approved credentials, then apply it.'
