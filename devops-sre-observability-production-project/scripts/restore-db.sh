#!/usr/bin/env bash
set -euo pipefail
FILE="${1:?Usage: ./scripts/restore-db.sh <sql-file>}"
PGHOST="${PGHOST:-localhost}"
PGPORT="${PGPORT:-5432}"
PGUSER="${PGUSER:-orders}"
PGDATABASE="${PGDATABASE:-order_management}"
PGPASSWORD="${PGPASSWORD:-change-me-local}"
export PGPASSWORD
psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" < "$FILE"
echo "Restore completed"
