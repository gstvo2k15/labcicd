#!/usr/bin/env bash
set -euo pipefail
AWS_REGION="${AWS_REGION:-us-east-1}"
for repo in k8s-docker-ecr/frontend k8s-docker-ecr/backend; do
  aws ecr describe-repositories --repository-names "$repo" --region "$AWS_REGION" >/dev/null 2>&1 || \
  aws ecr create-repository --repository-name "$repo" --region "$AWS_REGION" \
    --image-tag-mutability MUTABLE \
    --image-scanntestinglab.com-configuration scanOnPush=true >/dev/null
  echo "Ready: $repo"
done
