# Cosign image signing
For a local key pair: `cosign generate-key-pair`, then `cosign sign --key cosign.key IMAGE@DIGEST`. In CI, prefer OIDC/keyless signing so no long-lived private key is stored in the repository. Verify with `cosign verify --certificate-identity ... --certificate-oidc-issuer ... IMAGE@DIGEST` using the exact identity policy used by your organization.
