#!/usr/bin/env bash
set -euo pipefail
: "${DATABASE_URL:?Set DATABASE_URL}"
mkdir -p backups
pg_dump "$DATABASE_URL" --format=custom --file="backups/orders-$(date +%Y%m%d-%H%M%S).dump"
