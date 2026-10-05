#!/usr/bin/env bash
set -euo pipefail
PGHOST="${PGHOST:-localhost}"
PGPORT="${PGPORT:-5432}"
PGUSER="${PGUSER:-orders}"
PGDATABASE="${PGDATABASE:-order_management}"
PGPASSWORD="${PGPASSWORD:-change-me-local}"
export PGPASSWORD
mkdir -p backups
FILE="backups/order_management_$(date +%Y%m%d_%H%M%S).sql"
pg_dump -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" "$PGDATABASE" > "$FILE"
cp "$FILE" backups/order_management_latest.sql
echo "Backup written to $FILE"
