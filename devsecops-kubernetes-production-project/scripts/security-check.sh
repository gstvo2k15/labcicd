#!/usr/bin/env bash
set -euo pipefail
trivy config k8s/ --severity HIGH,CRITICAL
semgrep scan --config security/sast/.semgrep.yml app/
gitleaks detect --source . --config security/secrets/gitleaks.toml --redact
