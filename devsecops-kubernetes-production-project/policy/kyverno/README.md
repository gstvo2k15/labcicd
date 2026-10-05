# Kyverno
Install Kyverno in the cluster, then apply these policies. Start in Audit for a new environment, validate violations, and move to Enforce after remediation. Production policy additionally requires approved ACR registries and signed images; signature verification is environment-specific and should be implemented with Kyverno verifyImages and your Cosign identity/issuer.
