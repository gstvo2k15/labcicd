# Architecture
This project separates application source from deployment state. CI builds, tests, scans, generates an SBOM, signs immutable images, and publishes them to ACR. CI then changes the GitOps repository. Argo CD reconciles Git to AKS. Kubernetes admission policies enforce baseline security.
