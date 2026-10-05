#!/usr/bin/env bash
set -euo pipefail
test -f backups/order_management_latest.sql
echo "Backup artifact exists. Next: restore it into an isolated database and record RPO/RTO."
