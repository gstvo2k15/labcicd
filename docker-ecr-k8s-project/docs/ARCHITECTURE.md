# Architecture

## High-level design

```text
Internet
   |
Ingress / Azure Application Gateway
   |
Frontend Service
   |
3 x React/Nginx Pods
   |
/api proxy
   |
Backend Service
   |
3 x FastAPI Pods ---- HPA (3-8)
   |
PostgreSQL Service
   |
PostgreSQL Pod

CI/CD:
Git -> Build -> Trivy -> ECR -> Kubernetes/AKS -> Rolling Update
```

## Docker boundary

- `app/frontend/Dockerfile`: Node build stage + Nginx runtime.
- `app/backend/Dockerfile`: Python slim runtime, unprivileged UID 10001.
- `.dockerignore`: prevents unnecessary source and secret files from entering build context.

## Registry boundary

Amazon ECR stores the built artifacts. Version and commit-SHA tags make deployment history traceable.

## Kubernetes boundary

The cluster pulls private images through `ecr-registry-secret`. ECR authorization tokens expire, so the secret must be refreshed using a secure mechanism.

## Production note

For AKS, an enterprise design commonly uses Azure Container Registry for native cluster image pulls. If ECR is mandated, implement an approved cross-cloud identity/credential rotation pattern rather than placing long-lived AWS keys in Kubernetes.
