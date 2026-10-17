#!/usr/bin/env bash
set -Eeuo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
command -v openssl >/dev/null || { echo 'Install openssl.' >&2; exit 1; }

docker info >/dev/null
docker compose version

umask 077
[[ -f .env ]] || cp .env.example .env

mkdir -p secrets
chmod 700 secrets

if [[ ! -f secrets/grafana_admin_password.txt ]]; then
  openssl rand -hex 24 > secrets/grafana_admin_password.txt
fi

# Grafana (UID 472) must be able to read the Docker-mounted secret.
# The 0700 directory protects the file from other host users.
chmod 444 secrets/grafana_admin_password.txt
docker compose config --quiet
echo 'Configuration ready. Read the password with:'
echo 'cat secrets/grafana_admin_password.txt'
