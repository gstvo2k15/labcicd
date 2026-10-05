#!/usr/bin/env bash
set -euo pipefail
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
VERSION="${VERSION:-1.0.0}"
SHA="$(git rev-parse --short=12 HEAD 2>/dev/null || echo local)"

aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$REGISTRY"

for app in frontend backend; do
  REPO="$REGISTRY/k8s-docker-ecr/$app"
  docker build -f "app/$app/Dockerfile" -t "$REPO:$VERSION" .
  docker tag "$REPO:$VERSION" "$REPO:sha-$SHA"
  docker tag "$REPO:$VERSION" "$REPO:latest"
  docker push "$REPO:$VERSION"
  docker push "$REPO:sha-$SHA"
  docker push "$REPO:latest"
done
