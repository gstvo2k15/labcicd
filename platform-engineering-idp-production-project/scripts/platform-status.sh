#!/usr/bin/env bash
set -euo pipefail
: "${PLATFORM_API_URL:=http://localhost:8080}"
curl --fail --silent --show-error "$PLATFORM_API_URL/platform/status"; echo
