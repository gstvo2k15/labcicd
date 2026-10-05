# Secret scanning
`gitleaks detect --source . --config security/secrets/gitleaks.toml --redact` scans commits and the working tree. Real credentials must never be committed.
