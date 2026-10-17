#!/usr/bin/env bash
set -Eeuo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
command -v openssl >/dev/null || { echo 'Instala openssl.' >&2; exit 1; }

docker info >/dev/null
docker compose version

umask 077
[[ -f .env ]] || cp .env.example .env

mkdir -p secrets
chmod 700 secrets

if [[ ! -f secrets/grafana_admin_password.txt ]]; then
  openssl rand -hex 24 > secrets/grafana_admin_password.txt
fi

# Grafana (UID 472) debe poder leer el secreto montado por Docker.
# El directorio 0700 protege el archivo frente a otros usuarios del host.
chmod 444 secrets/grafana_admin_password.txt
docker compose config --quiet
echo 'Configuración preparada. Consulta la contraseña con:'
echo 'cat secrets/grafana_admin_password.txt'
