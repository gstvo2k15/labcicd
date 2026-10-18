# REAL-TIME DEVOPS PLATFORM ENGINEERtesttesttestinglab.comlab.comlab.com — INTERNAL DEVELOPER PLATFORM

A hands-on, GitHub-ready Platform Engineertesttestinglab.comlab.com project for an Order Management organization. The platform provides reusable **Golden Paths** so developers can create, secure, build, deploy, observe and operate services without repeattesttestinglab.comlab.com low-level Kubernetes/Azure work.

## 1. What you build

```text
Developer
  ↓
Backstage Developer Portal
  ↓
Golden Path / Software Template
  ↓
GitHub Repository
  ↓
Reusable CI → Tests → SAST → SCA → Gitleaks → Trivy → SBOM
  ↓
Azure Container Registry
  ↓
GitOps Repository
  ↓
Argo CD
  ↓
Azure AKS
  ↓
Order Management Service
  ↓
Prometheus / Grafana / Loki / Tempo / OpenTelemetry
```

## 2. Repository structure

```text
platform-engineertesttestinglab.comlab.com-idp/
├── backstage/                 # portal config, catalog and template
├── templates/                 # Golden Path starter docs/skeleton
├── platform-api/              # real FastAPI automation API
├── app/order-service/         # real runnable example service
├── helm/platform-service/     # reusable Helm Golden Chart
├── kubernetes/                # namespaces, quotas, RBAC, network policy
├── gitops/                    # dev/stagtesttestinglab.comlab.com/prod desired state + Argo app
├── terraform/                 # Azure modules for RG/VNet/AKS/ACR/monitortesttestinglab.comlab.com
├── pipelines/                 # reusable GitHub/Azure pipeline examples
├── security/                  # Semgrep/Gitleaks/security baseline
├── policy/kyverno/            # admission guardrails
├── observability/             # Prometheus/Grafana/Loki/Tempo/OTel examples
├── scripts/                   # real executable platform workflows
├── docs/                      # step-by-step hands-on guides
└── architecture/              # Mermaid diagrams
```

## 3. Prerequisites

Local:
- Docker + Docker Compose
- Git
- Python 3.12+
- curl

Azure/Kubernetes:
- Azure CLI
- Terraform >= 1.7
- kubectl
- Helm 3
- an Azure subscription

Optional security tooltesttestinglab.comlab.com:
- Trivy
- Syft
- Gitleaks
- Semgrep
- Cosign

## 4. HANDS-ON — run the platform locally

### Step 1: start the real Platform API and Order Service

```bash
git clone <your-repository-url> platform-engineertesttestinglab.comlab.com-idp
cd platform-engineertesttestinglab.comlab.com-idp
cp .env.example .env
docker compose build
docker compose up -d
docker compose ps
```

Health checks:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/platform/status
curl http://localhost:8081/health
```

Open API documentation:

```text
http://localhost:8080/docs
http://localhost:8081/docs
```

### Step 2: register a service through the Platform API

```bash
curl -X POST http://localhost:8080/services \
  -H 'Content-Type: application/json' \
  -d '{"name":"order-service","owner":"orders-team","lifecycle":"production","language":"python","environment":"dev","repository":"https://github.com/example/order-service"}'
```

Check:

```bash
curl http://localhost:8080/services
curl http://localhost:8080/services/order-service
```

### Step 3: request a deployment

```bash
curl -X POST http://localhost:8080/deploy \
  -H 'Content-Type: application/json' \
  -d '{"service":"order-service","environment":"dev","image":"example.azurecr.io/platform/order-service:1.0.0"}'
```

```bash
curl http://localhost:8080/deployments
```

### Step 4: test the example Order Service

```bash
curl -X POST http://localhost:8081/orders \
  -H 'Content-Type: application/json' \
  -d '{"customer_id":"user-100","items":[{"sku":"burger-1","quantity":2}]}'

curl http://localhost:8081/orders
```

Stop:

```bash
docker compose down
```

## 5. HANDS-ON — run without Docker

```bash
cd platform-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pytest
pytest -q
uvicorn app.main:app --reload --port 8080
```

In another terminal:

```bash
cd app/order-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt pytest
pytest -q
uvicorn main:app --reload --port 8081
```

## 6. Golden Path concept

A Golden Path is the platform team's supported, repeatable route:

```text
Choose template
→ enter service/team/environment
→ generate source + Dockerfile + tests + CI + Helm + catalog metadata
→ run security checks
→ build immutable image
→ push ACR
→ update GitOps
→ Argo CD sync
→ AKS
→ Backstage shows ownership and operational links
```

The goal is **self-service with guardrails**, not givtesttestinglab.comlab.com every developer cluster-admin access.

## 7. Backstage practice

This repo contains Backstage configuration examples in `backstage/` and a production microservice Scaffolder template in `backstage/templates/production-microservice/`.

Create a Backstage app with the official CLI:

```bash
npx @backstage/create-app@latest
cd my-backstage-app
yarn dev
```

Copy/adapt:

```text
backstage/app-config.yaml
backstage/catalog/groups.yaml
backstage/catalog/components.yaml
backstage/catalog/apis.yaml
backstage/templates/production-microservice/template.yaml
```

Register catalog locations from the Backstage UI or `app-config.yaml`.

The template collects:

```text
service name
owner/team
repository
environment
```

and demonstrates generation of catalog metadata, CI and deployment scaffoldtesttestinglab.comlab.com.

> Real GitHub repository creation requires a GitHub integration/token configured in Backstage. Never commit that token.

## 8. Reusable Helm Golden Chart

Validate:

```bash
helm lint helm/platform-service
helm template order-service helm/platform-service -f helm/platform-service/values-dev.yaml
```

Install a safe local example:

```bash
helm upgrade --install order-service helm/platform-service -n dev --create-namespace \
  -f helm/platform-service/values-dev.yaml \
  --set image.repository=nginx \
  --set image.tag=1.27-alpine
```

Check:

```bash
kubectl get deploy,svc,pods -n dev
kubectl rollout status deployment/order-service -n dev
```

## 9. Kubernetes platform foundation

Review manifests before applytesttestinglab.comlab.com:

```bash
kubectl apply -f kubernetes/namespaces.yaml
kubectl apply -f kubernetes/resourcequotas.yaml
kubectl apply -f kubernetes/limitranges.yaml
kubectl apply -f kubernetes/rbac.yaml
kubectl apply -f kubernetes/networkpolicies.yaml
```

Why:
- Namespace: isolation
- ResourceQuota: namespace capacity boundary
- LimitRange: safe default requests/limits
- RBAC: least privilege
- NetworkPolicy: reduce unnecessary network paths

## 10. Kyverno guardrails

Install Kyverno on a lab cluster, then:

```bash
kubectl apply -f policy/kyverno/require-labels.yaml
kubectl apply -f policy/kyverno/require-resources.yaml
kubectl apply -f policy/kyverno/disallow-privileged.yaml
kubectl apply -f policy/kyverno/disallow-latest-production.yaml
```

Test:

```bash
kubectl apply -f policy/kyverno/examples/bad-deployment.yaml
kubectl apply -f policy/kyverno/examples/good-deployment.yaml
```

The insecure deployment should be rejected where the policy is in Enforce mode.

## 11. Terraform — Azure platform

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# edit subscription_id, location, ACR and AKS names
cd terraform
terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
```

Provisioned modules:
- Resource Group root resource
- VNet + AKS subnet
- ACR
- AKS with managed identity, Azure CNI, Azure Policy, OIDC and Workload Identity
- Log Analytics

After practice:

```bash
terraform destroy
```

Use remote, secured Terraform state for real environments.

## 12. ACR and AKS

```bash
az login
az aks get-credentials --resource-group <rg> --name <aks>
az acr login --name <acr>
```

Build/push:

```bash
docker build -t <acr>.azurecr.io/platform/order-service:1.0.0 app/order-service
docker push <acr>.azurecr.io/platform/order-service:1.0.0
```

Production convention:

```text
1.0.0
sha-<commit>
<immutable-digest>
```

Do not use `latest` as the production source of truth.

## 13. GitOps + Argo CD

The desired state lives in `gitops/`:

```text
gitops/
├── environments/dev/order-service/values.yaml
├── environments/stagtesttestinglab.comlab.com/order-service/values.yaml
├── environments/production/order-service/values.yaml
└── applications/order-service-dev.yaml
```

Install Argo CD in a lab cluster, then:

```bash
kubectl apply -f gitops/applications/order-service-dev.yaml
kubectl get applications -n argocd
argocd app get order-service-dev
argocd app sync order-service-dev
```

Promotion:

```text
DEV → smoke tests → STAGtesttesttestinglab.comlab.comlab.com → integration tests → approval → PRODUCTION
```

## 14. Reusable CI / DevSecOps

GitHub reusable workflow:

```text
pipelines/templates/github-actions/service-ci.yml
```

It demonstrates:

```text
Checkout → tests → Gitleaks → Trivy → Docker build
```

Extend it in your environment with:
- Semgrep/SonarQube
- pip-audit/npm audit
- Syft SBOM
- Cosign signtesttestinglab.comlab.com
- ACR push ustesttestinglab.comlab.com OIDC/workload identity
- GitOps PR/update

Azure DevOps starter:

```text
pipelines/templates/azure-devops.yml
```

## 15. Observability standard

The platform standard is:

```text
service → metrics → Prometheus → Grafana
service stdout → Loki → Grafana
service → OpenTelemetry → Tempo → Grafana
```

Configuration examples:

```text
observability/prometheus/prometheus.yml
observability/grafana/datasources.yaml
observability/opentelemetry/collector.yaml
observability/loki/loki.yaml
observability/tempo/tempo.yaml
observability/alertmanager/alertmanager.yml
```

Every generated service should have health endpoints, structured logs and telemetry.

## 16. Automation scripts

```bash
./scripts/health-check.sh
./scripts/platform-status.sh
./scripts/create-service.sh inventory-service inventory-team https://github.com/example/inventory-service
./scripts/deploy-service.sh inventory-service dev example.azurecr.io/platform/inventory-service:1.0.0
```

Kubernetes rollback:

```bash
./scripts/rollback-service.sh dev order-service
```

## 17. Hands-on exercises

### Exercise A — create inventory-service

Create a FastAPI service with:
- `/health`
- `/ready`
- `/inventory/{sku}`
- tests
- Dockerfile
- catalog-info.yaml
- Helm values
- CI workflow
- GitOps entry

### Exercise B — new team

Create `inventory-team` and set:

```yaml
platform.company.io/team: inventory-team
platform.company.io/environment: dev
platform.company.io/cost-center: engineertesttestinglab.comlab.com
```

### Exercise C — policy

Change Kyverno to require `platform.company.io/cost-center` in stagtesttestinglab.comlab.com/production.

### Exercise D — self-service

Add a Backstage action that calls:

```text
POST /services
```

and returns the generated repository/service metadata.

### Exercise E — progressive delivery

Extend the Golden Chart with canary or blue/green support.

### Exercise F — cost visibility

Add OpenCost and map costs by namespace/team/environment.

## 18. Troubleshoottesttestinglab.comlab.com

### Backstage unavailable

```bash
kubectl get pods -n backstage
kubectl describe pod -n backstage <pod>
kubectl logs -n backstage <pod>
```

### Argo CD OutOfSync

```bash
argocd app get order-service-dev
argocd app diff order-service-dev
argocd app sync order-service-dev
```

### Kubernetes deployment failure

```bash
kubectl get pods -n dev
kubectl describe deployment order-service -n dev
kubectl rollout status deployment/order-service -n dev
kubectl logs -n dev deploy/order-service
```

### Kyverno rejection

```bash
kubectl get policyreport -A
kubectl describe policyreport -n dev
```

### ACR failure

```bash
az login
az acr login --name <acr>
az acr show --name <acr>
```

## 19. Platform access model

| Role | Responsibility |
|---|---|
| Platform Admin | platform-wide administration |
| Platform Engineer | modules, policies, templates, cluster platform |
| Developer | create services and operate allowed workloads |
| Viewer | read-only visibility |

Implement with Backstage permissions, Azure RBAC and Kubernetes RBAC. Avoid cluster-admin for normal developer workflows.

## 20. Disaster recovery

Back up and protect:
- Git repositories
- Terraform remote state
- Backstage configuration
- Argo CD configuration
- Key Vault recovery material
- application databases

Recovery order:

```text
Azure infrastructure → AKS → GitOps → Argo CD → secrets → workloads → observability → application validation
```

## 21. Interview explanation

> I built an Internal Developer Platform ustesttestinglab.comlab.com Backstage, reusable Golden Path templates, Terraform Azure modules, a standard Helm chart, reusable CI security controls, GitOps with Argo CD, Kyverno admission guardrails, service ownership metadata and observability integrations. Developers use self-service workflows while the platform team owns the standards, guardrails and runtime platform.

## 22. Security rules

Never commit:
- `.env`
- cloud credentials
- private keys
- kubeconfigs
- Terraform state containtesttestinglab.comlab.com secrets

Use Azure Workload Identity/OIDC and Key Vault for real environments.
