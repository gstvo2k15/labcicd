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
root="$(pwd -P)"
mkdir -p reports/.trivy-cache
failed=0

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
  safe_name="${image//[^a-zA-Z0-9_.-]/_}"
  docker image save --output "$scan_dir/image.tar" "$image"
  # No Docker socket. Use the host UID so reports are not owned by root.
  if ! docker run --rm --user "$(id -u):$(id -g)" \
    --mount "type=bind,source=$scan_dir,target=/scan,readonly" \
    --mount "type=bind,source=$root/reports,target=/reports" \
    --mount "type=bind,source=$root/reports/.trivy-cache,target=/cache" \
    --env TRIVY_CACHE_DIR=/cache \
    aquasec/trivy:0.69.3 image --input /scan/image.tar \
    --scanners vuln,secret --severity HIGH,CRITICAL --exit-code 1 \
    --format json --output "/reports/$safe_name.trivy.json"; then
    failed=1
  fi
  rm -f -- "$scan_dir/image.tar"
done

if (( failed )); then
  echo 'Security gate failed. Review Checkov output and reports/*.trivy.json.' >&2
  exit 1
fi

echo 'Checkov and Trivy passed.'
