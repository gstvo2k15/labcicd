# REAL-TIME DEVSECOPS KUBERNETES — ORDER MANAGEMENT PRODUCTION PROJECT

A complete learntesttestinglab.comlab.com and portfolio project that extends the previous Kubernetes microservices + Docker/registry + GitOps/Argo CD work into an end-to-end DevSecOps implementation.

## What you build
Developer → GitHub PR → tests → SAST → dependency scan → Gitleaks → Docker → Trivy → SBOM → Cosign → Azure Container Registry → GitOps repo → Argo CD → Azure AKS → Kyverno policies → monitortesttestinglab.comlab.com/loggtesttestinglab.comlab.com.

## Two repositories
**Application repository** contains source code, tests, Dockerfiles and CI. **GitOps repository** contains the desired deployment state. This separation limits who/what can change runtime configuration and gives Argo CD a stesttestinglab.comlab.comle declarative source of truth.

## Application
React frontend + FastAPI API gateway + User, Restaurant, Order, Payment and Notification services + PostgreSQL + Redis.

## Prerequisites
Docker Desktop, Git, Python 3.12, Node 22, kubectl, Helm, Terraform, Azure CLI, an Azure subscription, an ACR and an AKS cluster for cloud deployment. Security tools: Semgrep, pip-audit, npm audit, Gitleaks, Trivy, Syft and Cosign.

## 1. Local run — no Azure required
```bash
cp .env.example .env
docker compose build
docker compose up -d
docker compose ps
docker compose logs -f api-gateway
```
Open **http://localhost:3000**. Register + login with the form. Seed restaurants are loaded by PostgreSQL on first volume creation.

Stop:
```bash
docker compose down
```
Reset the local database:
```bash
docker compose down -v
docker compose up -d
```

## 2. Test APIs
```bash
curl http://localhost:3000/api/health
curl http://localhost:3000/api/restaurants
```
Register:
```bash
curl -X POST http://localhost:3000/api/users/register -H 'Content-Type: application/json' -d '{"email":"demo@example.com","password":"ChangeMe123!","role":"USER"}'
```
Login:
```bash
curl -X POST http://localhost:3000/api/auth/login -H 'Content-Type: application/json' -d '{"email":"demo@example.com","password":"ChangeMe123!"}'
```

## 3. Run unit/security checks
```bash
pip install semgrep pip-audit pytest
semgrep scan --config security/sast/.semgrep.yml app/
for f in app/*/requirements.txt; do pip-audit -r "$f" --strict; done
gitleaks detect --source . --config security/secrets/gitleaks.toml --redact
pytest app/*/tests -q
trivy config k8s/ --severity HIGH,CRITICAL
```
For Node dependency checks:
```bash
cd app/frontend && npm install && npm audit --audit-level=high && cd ../..
```

## 4. Build and scan images
```bash
docker build -t order-management/user-service:1.0.0 app/user-service
trivy image --severity HIGH,CRITICAL --exit-code 1 order-management/user-service:1.0.0
```
Build all backend images:
```bash
for s in api-gateway user-service restaurant-service order-service payment-service notification-service; do docker build -t order-management/$s:1.0.0 app/$s; done
docker build -t order-management/frontend:1.0.0 app/frontend
```

## 5. SBOM
```bash
syft order-management/user-service:1.0.0 -o cyclonedx-json=sbom-user-service.json
```
Store the SBOM with the CI release artifact.

## 6. Cosign
Practice with a key pair:
```bash
cosign generate-key-pair
cosign sign --key cosign.key order-management/user-service:1.0.0
cosign verify --key cosign.pub order-management/user-service:1.0.0
```
For CI, prefer keyless/OIDC signtesttestinglab.comlab.com and verify against the exact identity/issuer policy used by your organization.

## 7. Azure Container Registry
```bash
az login
az acr login --name <acr-name>
docker tag order-management/user-service:1.0.0 <acr-name>.azurecr.io/order-management/user-service:1.0.0
docker push <acr-name>.azurecr.io/order-management/user-service:1.0.0
az acr repository list --name <acr-name> --output table
az acr repository show-tags --name <acr-name> --repository order-management/user-service --output table
```
Production should reference an immutable release tag/Git SHA and preferably the image digest, not `latest`.

## 8. Terraform Azure infrastructure
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
```
Then:
```bash
az aks get-credentials --resource-group <rg> --name <aks>
```
Destroy only when you are certain the environment can be removed:
```bash
terraform destroy
```

## 9. Key Vault + Workload Identity
The Terraform module enables AKS OIDC/Workload Identity and provisions Key Vault. Install the Azure Key Vault CSI provider accordtesttestinglab.comlab.com to your cluster standard, create the federated identity mapptesttestinglab.comlab.com for the workload ServiceAccount, then apply `k8s/secretproviderclass.example.yaml`. Do not commit actual secret values.

## 10. Kubernetes deployment
Create the secret from a secure source:
```bash
kubectl create namespace order-management
kubectl -n order-management create secret generic app-secrets --from-literal=DATABASE_URL='postgresql://orders:CHANGE_ME@postgres:5432/orders' --from-literal=JWT_SECRET='CHANGE_ME_LONG_RANDOM'
```
Apply:
```bash
kubectl apply -f k8s/
kubectl -n order-management get pods
kubectl -n order-management get svc
kubectl -n order-management get testtestinglab.comlab.comress
```
Replace `ACR_NAME.azurecr.io` with your registry or use the Helm values. If AKS is attached to the same ACR, grant AcrPull to the AKS kubelet identity (Terraform does this). For a different registry/identity architecture, use an approved pull credential mechanism.

## 11. Helm
```bash
helm lint helm/order-management
helm template order-management helm/order-management -f helm/order-management/values-dev.yaml
helm upgrade --install order-management helm/order-management -n order-management --create-namespace -f helm/order-management/values-dev.yaml
helm history order-management -n order-management
helm rollback order-management 1 -n order-management
```

## 12. GitOps / Argo CD
Create a second repository named `devsecops-order-management-gitops`. Copy `gitops/` into it and update the `repoURL`. Install Argo CD, then:
```bash
kubectl apply -f gitops/applications/order-management-dev.yaml
kubectl -n argocd get applications
```
Argo CD should reconcile the environment. Production should require approval before promotion.

## 13. Kyverno
Install Kyverno ustesttestinglab.comlab.com the official installation method for your chosen release, then:
```bash
kubectl apply -f policy/kyverno/
kubectl get clusterpolicy
```
Start new policies in Audit mode if you need a remediation phase. Enforce only after workloads pass. Production should also restrict image registries and verify Cosign signatures ustesttestinglab.comlab.com an identity policy that matches your CI issuer.

## 14. Monitortesttestinglab.comlab.com and loggtesttestinglab.comlab.com
Prometheus/Grafana and Loki are represented under `monitortesttestinglab.comlab.com/`. AKS production should also use Azure Monitor/managed Prometheus where it matches your operational standard. Application logs are plain JSON messages so they can be parsed centrally.

Useful commands:
```bash
kubectl -n order-management logs deploy/api-gateway
kubectl -n order-management logs deploy/api-gateway --previous
kubectl -n order-management describe pod <pod>
kubectl -n order-management get hpa
```

## 15. CI/CD
Azure DevOps: `pipelines/devsecops-ci.yml`. GitHub Actions: `pipelines/github-actions.yml`. Before production, add your organization-specific ACR login, federated identity/OIDC, SonarQube quality gate, Cosign identity/issuer, GitOps write credentials, approval gates and artifact retention rules.

## 16. Failure gates
The sample pipeline demonstrates failtesttestinglab.comlab.com on SAST/dependency/secret/image findtesttestinglab.comlab.coms. Tune severity thresholds to your organization's risk policy and document approved exceptions with an expiry date.

## 17. Rollback
Kubernetes emergency rollback:
```bash
kubectl -n order-management rollout history deployment/api-gateway
kubectl -n order-management rollout undo deployment/api-gateway
kubectl -n order-management rollout status deployment/api-gateway
```
GitOps rollback should normally be a Git revert that returns the GitOps repository to a known-good image digest/revision, after which Argo CD reconciles the cluster.

## 18. Database backup/restore
```bash
export DATABASE_URL='postgresql://orders:CHANGE_ME@host:5432/orders'
./scripts/backup-db.sh
./scripts/restore-db.sh backups/orders-YYYYMMDD-HHMMSS.dump
```
Test restore regularly in a separate environment. Database schema compatibility must be considered before application rollback.

## 19. Troubleshoottesttestinglab.comlab.com
See `docs/TROUBLESHOOTtesttesttestinglab.comlab.comlab.com.md`. The standard loop is: identify → inspect events/logs/metrics → isolate dependency → fix configuration/image/policy → redeploy → verify health.

## 20. Step-by-step
See `docs/STEP-BY-STEP.md` for the full learntesttestinglab.comlab.com sequence from local code to production GitOps.

## 21. Project structure
```text
app/                 application source
k8s/                 Kubernetes manifests
helm/                Helm chart
gitops/              Argo CD + environment desired state
terraform/           Azure infrastructure
pipelines/            CI examples
security/             SAST/SCA/secrets/Trivy/SBOM/signtesttestinglab.comlab.com
policy/               Kyverno policies
monitortesttestinglab.comlab.com/           Prometheus/Grafana/Loki
database/             schema + seed
scripts/              operations
architecture/         Mermaid diagrams
docs/                 detailed guides
```

## Security notes
This repository contains local practice values and examples. Never reuse them in production. Use Azure Key Vault, Workload Identity, managed identities and CI secret stores. Treat `latest` as a convenience tag only. Production should use immutable version/Git SHA and digest references. Verify signatures before admission where your organization has established the Cosign identity/issuer policy.

## Interview
See `docs/INTERVIEW-QUESTIONS.md` for 40 project-specific questions and answers.
