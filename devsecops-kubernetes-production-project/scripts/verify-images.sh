#!/usr/bin/env bash
set -euo pipefail
: "${IMAGE:?Set IMAGE to an immutable image reference}"
trivy image --severity HIGH,CRITICAL "$IMAGE"
cosign verify "$IMAGE" >/dev/null
