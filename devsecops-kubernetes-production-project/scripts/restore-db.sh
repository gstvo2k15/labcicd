#!/usr/bin/env bash
set -euo pipefail
: "${DATABASE_URL:?Set DATABASE_URL}"
: "${1:?Usage: restore-db.sh backup.dump}"
pg_restore --clean --if-exists --dbname="$DATABASE_URL" "$1"
