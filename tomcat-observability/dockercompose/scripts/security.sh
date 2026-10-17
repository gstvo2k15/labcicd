#!/usr/bin/env bash

set -Eeuo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."

all_images=false

case "${1:-}" in
  '') ;;
  --all-images) all_images=true ;;
  *) echo 'Usage: bash scripts/security.sh [--all-images]' >&2; exit 2 ;;
esac

[[ $# -le 1 ]] || { echo 'Too many arguments.' >&2; exit 2; }
docker info >/dev/null
command -v jq >/dev/null || { echo 'Install jq to summarize security reports.' >&2; exit 1; }
root="$(pwd -P)"
mkdir -p reports/.trivy-cache
failed=0
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
  printf '### Trivy image checks\n\n| Image | HIGH/CRITICAL findings | Scanner exit |\n| --- | ---: | ---: |\n' >> "$GITHUB_STEP_SUMMARY"
fi

# Checkov checks the Dockerfile; Trivy scans the built image.
if ! docker run --rm --mount "type=bind,source=$root,target=/src,readonly" \
  bridgecrew/checkov:3.2.471 --directory /src/tomcat --framework dockerfile --compact; then
  failed=1
fi

docker compose build --pull tomcat
images=('lab/tomcat-alpine-jdk17:10.1.61')

if "$all_images"; then
  docker compose pull --ignore-buildable
  image_list="$(docker compose config --images | sort -u)"
  mapfile -t images <<< "$image_list"
fi

# Private temporary directory: exported image archives may contain secrets.
scan_dir="$(mktemp -d "$root/reports/.scan.XXXXXXXX")"
trap 'rm -f -- "$scan_dir/image.tar"; rmdir -- "$scan_dir"' EXIT

for image in "${images[@]}"; do
  echo "Scanning image: $image"
  safe_name="${image//[^a-zA-Z0-9_.-]/_}"
  report="reports/$safe_name.trivy.json"
  # Do not mistake a previous run's report for the result of a failed scan.
  rm -f -- "$report"
  docker image save --output "$scan_dir/image.tar" "$image"
  # No Docker socket. Use the host UID so reports are not owned by root.
  scan_status=0
  docker run --rm --user "$(id -u):$(id -g)" \
    --mount "type=bind,source=$scan_dir,target=/scan,readonly" \
    --mount "type=bind,source=$root/reports,target=/reports" \
    --mount "type=bind,source=$root/reports/.trivy-cache,target=/cache" \
    --env TRIVY_CACHE_DIR=/cache \
    aquasec/trivy:0.76.0 image --input /scan/image.tar \
    --scanners vuln,secret --severity HIGH,CRITICAL --exit-code 1 \
    --format json --output "/reports/$safe_name.trivy.json" || scan_status=$?

  if [[ ! -s "$report" ]] || ! jq -e '
    (.SchemaVersion | type == "number") and (.Results | type == "array")
  ' "$report" >/dev/null 2>&1; then
    echo "ERROR: Trivy did not produce a valid report for $image (exit $scan_status). Check scanner/download errors above." >&2
    if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
      printf '| `%s` | Scan error / missing report | %s |\n' "$image" "$scan_status" >> "$GITHUB_STEP_SUMMARY"
    fi
    failed=1
  else
    # Print actionable fields in Actions logs. Never print secret matches or source lines.
    jq -r '
      ["TARGET", "ID", "SEVERITY", "PACKAGE / RULE", "INSTALLED", "FIXED"],
      (.Results[] | .Target as $target |
        (.Vulnerabilities[]? | [$target, .VulnerabilityID, .Severity,
          .PkgName, .InstalledVersion, (.FixedVersion // "" | if . == "" then "no fix listed" else . end)]),
        (.Secrets[]? | [$target, "SECRET", .Severity, .RuleID, "redacted", "remove and rotate"]))
      | @tsv
    ' "$report"
    findings="$(jq '[.Results[] | (.Vulnerabilities[]?, .Secrets[]?) |
      select(.Severity == "HIGH" or .Severity == "CRITICAL")] | length' "$report")"
    echo "$image: $findings HIGH/CRITICAL findings; Trivy exit code $scan_status. Report: $report"
    if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
      printf '| `%s` | %s | %s |\n' "$image" "$findings" "$scan_status" >> "$GITHUB_STEP_SUMMARY"
    fi
    if (( findings > 0 )); then
      failed=1
    elif (( scan_status != 0 )); then
      echo "ERROR: Trivy failed for $image without reported HIGH/CRITICAL findings; inspect scanner errors above." >&2
      failed=1
    fi
  fi
  rm -f -- "$scan_dir/image.tar"
done

if (( failed )); then
  echo 'Security gate failed. Review Checkov output and reports/*.trivy.json.' >&2
  exit 1
fi

echo 'Checkov and Trivy passed.'
