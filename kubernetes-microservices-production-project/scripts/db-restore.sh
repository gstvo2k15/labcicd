#!/usr/bin/env bash
set -euo pipefail
FILE=${1:?backup SQL file required}
kubectl -n food-delivery cp "$FILE" "$(kubectl -n food-delivery get pod -l app=postgres -o jsonpath='{.items[0].metadata.name}'):/tmp/restore.sql"
POD=$(kubectl -n food-delivery get pod -l app=postgres -o jsonpath='{.items[0].metadata.name}')
kubectl -n food-delivery exec "$POD" -- psql -U "${POSTGRES_USER:-food}" -d "${POSTGRES_DB:-fooddb}" -f /tmp/restore.sql
