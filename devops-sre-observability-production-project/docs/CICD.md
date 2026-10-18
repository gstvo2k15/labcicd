# CICD

CI order is tests → SAST → dependency scan → secret scan → build → Trivy → SBOM → signtestinglab.com → ACR → GitOps.
