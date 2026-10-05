#!/usr/bin/env bash
set -euo pipefail
: "${PLATFORM_API_URL:=http://localhost:8080}"
SERVICE="${1:?service}"; ENV="${2:?environment}"; IMAGE="${3:?image}"
curl --fail --silent --show-error -X POST "$PLATFORM_API_URL/deploy" -H 'Content-Type: application/json' -d "{"service":"$SERVICE","environment":"$ENV","image":"$IMAGE"}"; echo
