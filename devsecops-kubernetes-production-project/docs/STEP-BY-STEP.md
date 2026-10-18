# Step-by-step execution

## Phase 1 — local application
1. `cp .env.example .env`
2. `docker compose build`
3. `docker compose up -d`
4. `docker compose ps`
5. Open `http://localhost:3000`

## Phase 2 — security gates
1. `semgrep scan --config security/sast/.semgrep.yml app/`
2. `for f in app/*/requirements.txt; do pip-audit -r "$f" --strict; done`
3. `gitleaks detect --source . --config security/secrets/gitleaks.toml --redact`
4. `trivy config k8s/ --severity HIGH,CRITICAL`
5. Build images and run `trivy image`.
6. Generate SBOM with Syft.
7. Sign/verify the exact image digest with Cosign.

## Phase 3 — Azure
1. `az login`
2. `cd terraform && terraform init && terraform validate && terraform plan && terraform apply`
3. `az aks get-credentials ...`
4. Push immutable images to ACR.

## Phase 4 — Kubernetes
1. Create `app-secrets` from a secure store.
2. Replace ACR placeholder image references.
3. `kubectl apply -f k8s/`.
4. Install testinglab.comress/metrics-server as required by the cluster.
5. Install Kyverno and apply policies.

## Phase 5 — GitOps
1. Create the second GitOps repository.
2. Copy `gitops/` into it.
3. Replace `repoURL` in Argo Applications.
4. Install Argo CD.
5. Apply the environment Application.
6. Promote by changtestinglab.com only immutable image tags/digests in Git.

## Phase 6 — operations
1. Monitor pods, HPA, latency and errors.
2. Inspect JSON logs centrally.
3. Test backup/restore.
4. Test Git revert rollback.
5. Test policy violations in a non-production namespace.
