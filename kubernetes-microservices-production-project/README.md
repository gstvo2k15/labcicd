# Real-Time Kubernetes Microservices — Production DevOps Project

A runnable learning project for an online food-delivery platform: React frontend + API Gateway + five FastAPI microservices + PostgreSQL + Redis, packaged with Docker, Kubernetes, Helm, Terraform/AKS, CI/CD, security and observability examples.

## Architecture
Application flow: **User → Ingress → React/API Gateway → microservices → PostgreSQL/Redis**. Delivery flow: **Git push → tests → Docker build → Trivy scan → ACR → AKS rollout → smoke test**.

## Prerequisites
Docker, Docker Compose, Python 3.12+, Node 22+, kubectl, Helm 3, Azure CLI, Terraform, Trivy, an Azure subscription.

## 1. Run locally
```bash
docker compose build
docker compose up -d
docker compose ps
docker compose logs -f api-gateway
```
Open `http://localhost:8080`. Gateway health: `http://localhost:8000/health`.

## 2. Useful Docker commands
```bash
docker compose logs

docker compose logs -f

docker compose down
REGISTRY=myacr.azurecr.io TAG=1.0.0 ./scripts/build-images.sh
```

## 3. Image tags
Use `service:1.0.0`, `service:sha-<commit>`, and `latest` for development. Production should deploy an immutable version/SHA or digest, not `latest`.

## 4. Terraform + AKS
```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
az aks get-credentials -g rg-food-delivery-prod -n aks-food-delivery
```
The Terraform example creates a resource group, VNet/subnet, AKS, ACR, Log Analytics and ACR pull role assignment. Review cost, SKU, region and security requirements before production use.

## 5. Build and push to ACR
```bash
az acr login --name <acr-name>
REGISTRY=<acr-login-server> TAG=1.0.0 ./scripts/build-images.sh
REGISTRY=<acr-login-server> TAG=1.0.0 ./scripts/push-images.sh
```

## 6. Kubernetes
Edit `k8s/secret.example.yaml` using your approved secret process; never commit real secrets. Replace `YOUR_ACR` in image names or use Helm values.
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.example.yaml
kubectl apply -f k8s/rbac.yaml -f k8s/postgres.yaml -f k8s/redis.yaml
kubectl apply -f k8s/api-gateway.yaml -f k8s/user-service.yaml -f k8s/restaurant-service.yaml -f k8s/order-service.yaml -f k8s/payment-service.yaml -f k8s/notification-service.yaml -f k8s/frontend.yaml
kubectl apply -f k8s/hpa.yaml -f k8s/ingress.yaml -f k8s/network-policy.yaml
kubectl -n food-delivery get pods,svc,ingress,hpa
```

## 7. Helm
```bash
helm lint helm/food-delivery
helm template food-delivery helm/food-delivery
helm upgrade --install food-delivery helm/food-delivery -n food-delivery --create-namespace --set registry=<acr-login-server> --set imageTag=1.0.0
helm rollback food-delivery 1
helm uninstall food-delivery -n food-delivery
```

## 8. Security
```bash
trivy image --severity HIGH,CRITICAL --ignore-unfixed <image>
```
Review `security/`, RBAC, NetworkPolicy and container security contexts. Use Key Vault/CSI or another approved secret manager in production.

## 9. Monitoring and logs
```bash
kubectl -n food-delivery logs deployment/order-service
kubectl -n food-delivery logs -f deployment/api-gateway
kubectl -n food-delivery logs --previous <pod>
kubectl -n food-delivery describe pod <pod>
kubectl -n food-delivery get hpa
```
Prometheus and Grafana guidance is under `monitoring/` and `docs/MONITORING.md`.

## 10. Rollout and rollback
```bash
kubectl -n food-delivery rollout status deployment/order-service
kubectl -n food-delivery rollout history deployment/order-service
./scripts/rollback.sh order-service
```

## 11. Database backup/restore
```bash
./scripts/db-backup.sh
./scripts/db-restore.sh backups/<file>.sql
```
Store backups outside the cluster and test restores regularly.

## AWS EKS / GCP GKE equivalents
Use EKS instead of AKS with ECR for AWS, or GKE with Artifact Registry for GCP. The Kubernetes workload layer remains broadly the same; replace identity, load balancer, networking, storage and registry integration with the cloud-native equivalent.

## Interview explanation
Explain the project as two flows: the **runtime flow** (Ingress → Gateway → microservices → data stores) and the **delivery flow** (Git → test → build → scan → registry → AKS → rollout). Discuss probes, HPA, PDB, NetworkPolicy, immutable tags, rollback, backup/restore and observability.

## Interview questions
1. Why use an API Gateway? 2. Why readiness vs liveness? 3. Why HPA? 4. How do you prevent `latest` drift? 5. How do services discover each other? 6. How do you secure secrets? 7. What causes ImagePullBackOff? 8. How do you roll back safely? 9. How do you handle DB failure? 10. What metrics drive capacity planning?

## Cleanup
```bash
helm uninstall food-delivery -n food-delivery || true
terraform -chdir=terraform destroy
```
Review resources before destroy.
