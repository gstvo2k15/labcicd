#!/usr/bin/env bash
set -euo pipefail
mkdir -p backups
kubectl -n food-delivery exec deploy/postgres -- pg_dump -U "${POSTGRES_USER:-food}" "${POSTGRES_DB:-fooddb}" > "backups/fooddb-$(date +%Y%m%d-%H%M%S).sql"
echo "Backup created under backups/"
