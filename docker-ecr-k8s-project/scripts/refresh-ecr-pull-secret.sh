#!/usr/bin/env bash
set -euo pipefail
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
NAMESPACE="${K8S_NAMESPACE:-k8s-ecr-app}"

kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
aws ecr get-login-password --region "$AWS_REGION" | \
kubectl create secret docker-registry ecr-registry-secret \
  --namespace "$NAMESPACE" \
  --docker-server="$REGISTRY" \
  --docker-username=AWS \
  --docker-password-stdin \
  --dry-run=client -o yaml | kubectl apply -f -

echo "ECR pull secret refreshed in namespace $NAMESPACE."
echo "ECR auth tokens expire after 12 hours; refresh before expiry or automate the rotation securely."
