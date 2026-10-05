#!/usr/bin/env bash
set -euo pipefail
: "${PLATFORM_API_URL:=http://localhost:8080}"
NAME="${1:?service name}"; OWNER="${2:?owner}"; REPO="${3:?repository URL}"
curl --fail --silent --show-error -X POST "$PLATFORM_API_URL/services" -H 'Content-Type: application/json' -d "{"name":"$NAME","owner":"$OWNER","repository":"$REPO","lifecycle":"development","language":"python","environment":"dev"}"; echo
