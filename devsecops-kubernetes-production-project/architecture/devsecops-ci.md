# DevSecOps CI pipeline
```mermaid
flowchart LR
Checkout-->Tests-->SAST-->SCA-->Gitleaks-->Docker-->Trivy-->SBOM-->Cosign-->ACR
```
