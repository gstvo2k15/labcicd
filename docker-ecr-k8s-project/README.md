# Real-Time Docker → Amazon ECR → Kubernetes Production Deployment

A hands-on DevOps project based on the earlier Kubernetes 3-tier application: **React frontend + Python/FastAPI backend + PostgreSQL**. The main learntestinglab.com path is **application code → Docker → security scan → Amazon ECR → Kubernetes/AKS**.

## 1. What you will build

```text
Developer
   |
   | git push
   v
CI/CD Pipeline
   |
   +--> Docker Build
   |
   +--> Trivy Security Scan
   |
   +--> Amazon ECR
   |       +-- frontend:1.0.x
   |       +-- frontend:sha-<commit>
   |       +-- backend:1.0.x
   |       +-- backend:sha-<commit>
   |
   v
AKS / Kubernetes
   |
   +--> Ingress --> Frontend Service --> Frontend Pods
   |                                  |
   |                                  +--> /api --> Backend Service --> Backend Pods
   |                                                               |
   |                                                               +--> PostgreSQL
   |
   +--> HPA + Probes + NetworkPolicy + Resources
```

## 2. Folder structure

```text
k8s-docker-ecr-project/
├── app/
│   ├── frontend/
│   │   ├── src/main.jsx
│   │   ├── src/style.css
│   │   ├── index.html
│   │   ├── package.json
│   │   ├── Dockerfile
│   │   └── .dockerignore
│   └── backend/
│       ├── main.py
│       ├── requirements.txt
│       ├── Dockerfile
│       └── .dockerignore
├── docker/
│   └── frontend/nginx.conf
├── docker-compose.yml
├── k8s/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.example.yaml
│   ├── app-secret.example.env
│   ├── postgres.yaml
│   ├── backend.yaml
│   ├── frontend.yaml
│   ├── hpa.yaml
│   ├── testinglab.comress.yaml
│   └── network-policy.yaml
├── helm/docker-ecr-app/
├── terraform/
├── pipelines/
├── scripts/
├── security/
├── monitortestinglab.com/
├── docs/
└── README.md
```

## 3. Prerequisites

Install:

- Docker Desktop / Docker Engine
- Docker Compose v2
- Git
- AWS CLI v2
- kubectl
- Helm 3
- Terraform 1.7+
- An AWS account with ECR permissions
- An AKS cluster if you want cloud deployment
- An Ingress controller and Metrics Server on the cluster for the optional Ingress/HPA steps

Verify:

```bash
docker --version
docker compose version
aws --version
kubectl version --client
helm version
terraform version
git --version
```

## 4. Application flow

The frontend is a React application compiled into static files. Nginx serves those files on port 8080 and proxies `/api/*` to the backend service named `backend`.

The backend is FastAPI on port 8000. It exposes `/health`, `/ready`, `/api/info`, `/api/messages` and `/api/echo`.

PostgreSQL stores messages created by `/api/echo`.

## 5. Run locally with Docker Compose

From the repository root:

```bash
docker compose build
docker compose up -d
docker compose ps
```

Test backend:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/api/info
```

Test frontend:

```text
http://localhost:8080
```

Test the API through the frontend proxy:

```bash
curl http://localhost:8080/api/info
curl -X POST http://localhost:8080/api/echo \
  -H 'Content-Type: application/json' \
  -d '{"message":"hello from Docker"}'
curl http://localhost:8080/api/messages
```

View logs:

```bash
docker compose logs -f frontend
docker compose logs -f backend
```

Stop:

```bash
docker compose down
```

## 6. Build Docker images manually

Backend:

```bash
docker build -f app/backend/Dockerfile -t k8s-docker-ecr/backend:1.0.0 app/backend
```

Frontend:

```bash
docker build -f app/frontend/Dockerfile -t k8s-docker-ecr/frontend:1.0.0 app/frontend
```

List images:

```bash
docker images | grep k8s-docker-ecr
```

Run backend:

```bash
docker run --rm -p 8000:8000 \
  -e DATABASE_URL='postgresql://appuser:apppassword@host.docker.internal:5432/appdb' \
  k8s-docker-ecr/backend:1.0.0
```

Run the frontend image:

```bash
docker run --rm -p 8080:8080 k8s-docker-ecr/frontend:1.0.0
```

## 7. Docker image taggtestinglab.com strategy

Use three tag types durtestinglab.com practice:

```text
1.0.0             human-readable release
sha-a1b2c3d4e5f6  immutable build identity
latest            convenience tag for development/demo only
```

Example:

```bash
docker tag k8s-docker-ecr/backend:1.0.0 k8s-docker-ecr/backend:sha-a1b2c3d4e5f6
docker tag k8s-docker-ecr/backend:1.0.0 k8s-docker-ecr/backend:latest
```

Production recommendation: deploy an immutable commit-SHA or digest rather than `latest`. If ECR tag immutability is enabled, do not repeatedly overwrite the same release tag.

## 8. Security scan before ECR

Use Trivy locally:

```bash
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:0.58.1 image --severity HIGH,CRITICAL --exit-code 1 \
  k8s-docker-ecr/backend:1.0.0

docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:0.58.1 image --severity HIGH,CRITICAL --exit-code 1 \
  k8s-docker-ecr/frontend:1.0.0
```

The pipeline uses the same gate. A HIGH/CRITICAL findtestinglab.com causes the build to fail unless your policy intentionally handles it differently.

## 9. Create Amazon ECR repositories

Set the AWS region:

```bash
export AWS_REGION=us-east-1
```

Confirm identity:

```bash
aws sts get-caller-identity
```

Create repositories:

```bash
aws ecr create-repository \
  --repository-name k8s-docker-ecr/frontend \
  --region "$AWS_REGION" \
  --image-scanntestinglab.com-configuration scanOnPush=true

aws ecr create-repository \
  --repository-name k8s-docker-ecr/backend \
  --region "$AWS_REGION" \
  --image-scanntestinglab.com-configuration scanOnPush=true
```

Or run:

```bash
./scripts/create-ecr-repositories.sh
```

For a production repository, prefer tag immutability and a lifecycle policy. The included Terraform can create both repositories and lifecycle policies.

## 10. Terraform ECR setup

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

For strict production-style immutable tags:

```bash
terraform apply -var='image_tag_mutability=IMMUTABLE'
```

Then return to the project root:

```bash
cd ..
```

## 11. Authenticate Docker to ECR

```bash
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws ecr get-login-password --region "$AWS_REGION" | \
  docker login --username AWS --password-stdin \
  "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
```

The ECR authorization token is temporary; do not hard-code it into source control.

## 12. Tag and push images

```bash
REGISTRY="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

# Version tags
docker tag k8s-docker-ecr/backend:1.0.0 "$REGISTRY/k8s-docker-ecr/backend:1.0.0"
docker tag k8s-docker-ecr/frontend:1.0.0 "$REGISTRY/k8s-docker-ecr/frontend:1.0.0"

# Commit tag
git_sha=$(git rev-parse --short=12 HEAD)
docker tag k8s-docker-ecr/backend:1.0.0 "$REGISTRY/k8s-docker-ecr/backend:sha-$git_sha"
docker tag k8s-docker-ecr/frontend:1.0.0 "$REGISTRY/k8s-docker-ecr/frontend:sha-$git_sha"

# Optional development tag
docker tag k8s-docker-ecr/backend:1.0.0 "$REGISTRY/k8s-docker-ecr/backend:latest"
docker tag k8s-docker-ecr/frontend:1.0.0 "$REGISTRY/k8s-docker-ecr/frontend:latest"
```

Push:

```bash
docker push "$REGISTRY/k8s-docker-ecr/backend:1.0.0"
docker push "$REGISTRY/k8s-docker-ecr/backend:sha-$git_sha"
docker push "$REGISTRY/k8s-docker-ecr/backend:latest"

docker push "$REGISTRY/k8s-docker-ecr/frontend:1.0.0"
docker push "$REGISTRY/k8s-docker-ecr/frontend:sha-$git_sha"
docker push "$REGISTRY/k8s-docker-ecr/frontend:latest"
```

Or run:

```bash
VERSION=1.0.0 AWS_REGION=us-east-1 ./scripts/build-and-push.sh
```

## 13. Verify ECR images

```bash
aws ecr describe-images \
  --repository-name k8s-docker-ecr/backend \
  --region "$AWS_REGION"

aws ecr describe-images \
  --repository-name k8s-docker-ecr/frontend \
  --region "$AWS_REGION"
```

## 14. ECR image scanntestinglab.com and lifecycle

ECR can scan images for vulnerabilities. Basic scanntestinglab.com focuses on OS vulnerabilities; enhanced scanntestinglab.com integrates with Amazon Inspector and can continuously scan OS and programmtestinglab.com-language package vulnerabilities.

For this project, use scan-on-push for a simple practice gate and enable enhanced/continuous scanntestinglab.com where your production security program requires it.

Lifecycle policy prevents unlimited image growth. The included policy keeps recent `sha-*` images and removes old untagged images. Review lifecycle policy previews before applytestinglab.com changes in a production repository.

## 15. Prepare Kubernetes secrets

Never commit the real database password or ECR token.

Create the application secret:

```bash
export K8S_NAMESPACE=k8s-ecr-app
export DB_PASSWORD='replace-with-a-strong-password'
./scripts/create-app-secret.sh
```

Refresh the ECR pull secret:

```bash
AWS_REGION=us-east-1 ./scripts/refresh-ecr-pull-secret.sh
```

Important: ECR Docker authorization tokens are valid for 12 hours. A manually created `imagePullSecret` therefore needs a refresh strategy. For a real production AKS environment, use a short-lived credential automation pattern or, preferably, publish the production image to a registry that the AKS workload can access through your enterprise identity design (commonly ACR for AKS). Do not store long-lived AWS access keys in a Kubernetes Secret.

## 16. Deploy PostgreSQL and application

Create namespace/config:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
```

Create PostgreSQL secret. The example manifest contains `CHANGE_ME`; replace it before applytestinglab.com:

```bash
kubectl -n k8s-ecr-app create secret generic postgres-secret \
  --from-literal=POSTGRES_DB=appdb \
  --from-literal=POSTGRES_USER=appuser \
  --from-literal=POSTGRES_PASSWORD="$DB_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -
```

Create application DB URL:

```bash
./scripts/create-app-secret.sh
```

Refresh ECR authentication:

```bash
./scripts/refresh-ecr-pull-secret.sh
```

Deploy:

```bash
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/network-policy.yaml
```

Optional Ingress:

```bash
kubectl apply -f k8s/testinglab.comress.yaml
```

Watch rollout:

```bash
kubectl -n k8s-ecr-app rollout status deployment/postgres
kubectl -n k8s-ecr-app rollout status deployment/backend
kubectl -n k8s-ecr-app rollout status deployment/frontend
```

Check:

```bash
kubectl -n k8s-ecr-app get pods -o wide
kubectl -n k8s-ecr-app get svc
kubectl -n k8s-ecr-app get hpa
```

## 17. Deploy with Helm

First create the namespace and secrets as above.

Update `helm/docker-ecr-app/values.yaml` with your registry and tag.

```bash
helm upgrade --install docker-ecr-app ./helm/docker-ecr-app \
  --namespace k8s-ecr-app \
  --create-namespace
```

Deploy a commit-specific image:

```bash
helm upgrade --install docker-ecr-app ./helm/docker-ecr-app \
  --namespace k8s-ecr-app \
  --set backend.tag=sha-a1b2c3d4e5f6 \
  --set frontend.tag=sha-a1b2c3d4e5f6
```

## 18. Rolltestinglab.com update

Never use a mutable tag as the only production deployment identity.

Example:

```bash
kubectl -n k8s-ecr-app set image deployment/backend \
  backend="$REGISTRY/k8s-docker-ecr/backend:sha-a1b2c3d4e5f6"

kubectl -n k8s-ecr-app rollout status deployment/backend
kubectl -n k8s-ecr-app rollout history deployment/backend
```

Rollback:

```bash
kubectl -n k8s-ecr-app rollout undo deployment/backend
```

## 19. CI/CD flow

```text
Git Push
   |
   v
Build frontend/backend images
   |
   v
Trivy HIGH/CRITICAL gate
   |
   v
Authenticate to ECR
   |
   v
Push version + commit-SHA tags
   |
   v
ECR scan / policy checks
   |
   v
Deploy immutable image to AKS
   |
   v
Kubernetes rolltestinglab.com update
   |
   v
Health checks + HPA + monitortestinglab.com
```

The main Azure DevOps pipeline is `pipelines/azure-pipelines.yml`.

### Azure DevOps variables

For practice, create secret pipeline variables:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

Also set `AWS_REGION` and `ECR_REPO_PREFIX` as non-secret variables.

Production recommendation: replace long-lived AWS access keys with federated/OIDC credentials or an approved enterprise secret-management integration.

## 20. Kubernetes pulltestinglab.com from private ECR

Kubernetes uses:

```yaml
spec:
  imagePullSecrets:
    - name: ecr-registry-secret
```

The secret is created from an ECR authorization token. The token is temporary, so it must be refreshed before expiry.

The included deployment manifests already reference the secret.

For production, consider one of these patterns:

1. **Practice / lab:** manually refresh the ECR pull secret.
2. **Automated lab:** run a tightly controlled credential-refresh mechanism with short-lived AWS credentials and strong RBAC.
3. **Enterprise production:** use ACR as the AKS-native production registry or establish an approved cross-cloud identity/registry architecture. Keep ECR as the AWS distribution/security source if required.
4. **Advanced:** use image replication/promote-and-deploy workflows so the cluster does not depend directly on an expirtestinglab.com ECR token.

## 21. Troubleshoottestinglab.com

### ImagePullBackOff

```bash
kubectl -n k8s-ecr-app get pod
kubectl -n k8s-ecr-app describe pod <pod-name>
```

Look for:

- wrong registry/account/region
- wrong repository name
- wrong image tag
- expired ECR pull secret
- misstestinglab.com `imagePullSecrets`
- node/network/DNS problems

Refresh the secret:

```bash
./scripts/refresh-ecr-pull-secret.sh
kubectl -n k8s-ecr-app rollout restart deployment/backend
kubectl -n k8s-ecr-app rollout restart deployment/frontend
```

### ErrImagePull

Verify the exact image:

```bash
kubectl -n k8s-ecr-app get deployment backend -o jsonpath='{.spec.template.spec.containers[0].image}'
aws ecr describe-images --repository-name k8s-docker-ecr/backend --region "$AWS_REGION"
```

### ECR authentication failure

```bash
aws sts get-caller-identity
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$REGISTRY"
```

The IAM principal needs ECR authorization and push/pull permissions appropriate to the operation.

### Incorrect image tag

```bash
docker images
git rev-parse --short=12 HEAD
aws ecr describe-images --repository-name k8s-docker-ecr/backend --region "$AWS_REGION"
```

Make sure the Kubernetes manifest points to a tag that actually exists.

### Docker build failure

```bash
docker build --no-cache --progress=plain -f app/backend/Dockerfile app/backend
docker build --no-cache --progress=plain -f app/frontend/Dockerfile app/frontend
```

Check build context and `.dockerignore`. For frontend problems, verify Node/npm versions and dependency installation.

### ECR push failure

```bash
aws sts get-caller-identity
aws ecr describe-repositories --repository-name k8s-docker-ecr/backend --region "$AWS_REGION"
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$REGISTRY"
docker push "$REGISTRY/k8s-docker-ecr/backend:1.0.0"
```

Typical causes: wrong account/region, repository misstestinglab.com, insufficient IAM permissions, expired login token, or network/proxy restrictions.

### Container crashes / CrashLoopBackOff

```bash
kubectl -n k8s-ecr-app logs deployment/backend --tail=100
kubectl -n k8s-ecr-app logs <pod> --previous
kubectl -n k8s-ecr-app describe pod <pod>
```

Check environment variables, database connectivity, startup command, permissions and probes.

### Backend not ready

```bash
kubectl -n k8s-ecr-app exec deploy/backend -- python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/ready').read())"
kubectl -n k8s-ecr-app get endpoints backend
kubectl -n k8s-ecr-app logs deploy/backend
```

### 502 / 503 from frontend/Ingress

```bash
kubectl -n k8s-ecr-app get testinglab.comress
kubectl -n k8s-ecr-app get svc
kubectl -n k8s-ecr-app get endpoints frontend backend
kubectl -n k8s-ecr-app logs deploy/frontend
```

### OOMKilled

```bash
kubectl -n k8s-ecr-app describe pod <pod>
kubectl -n k8s-ecr-app top pods
```

Increase the memory limit only after identifytestinglab.com the workload. Do not blindly increase limits.

## 22. Security best practices implemented

- Multi-stage frontend build.
- Small `alpine`/`slim` base images.
- Backend runs as UID 10001.
- No credentials in Dockerfiles.
- `.dockerignore` reduces build context.
- Kubernetes resource requests and limits.
- Readiness/liveness probes.
- Rolltestinglab.com updates.
- HPA.
- NetworkPolicy example.
- ECR scan-on-push.
- ECR lifecycle policy.
- Least-privilege ECR push policy example.
- Prefer immutable image tags/digests in production.
- Do not put AWS access keys in Docker images or Git.
- Use short-lived credentials and federated identity where possible.

## 23. Cleanup

Docker:

```bash
docker compose down --remove-orphans
docker image prune
```

Kubernetes:

```bash
kubectl delete namespace k8s-ecr-app
```

ECR:

```bash
aws ecr delete-repository --repository-name k8s-docker-ecr/frontend --region "$AWS_REGION" --force
aws ecr delete-repository --repository-name k8s-docker-ecr/backend --region "$AWS_REGION" --force
```

Terraform:

```bash
cd terraform
terraform destroy
```

## 24. Interview explanation

**Question: Explain your Docker-to-Kubernetes production flow.**

Answer:

> Developers push application code to Git. The CI pipeline builds separate frontend and backend Docker images ustestinglab.com production Dockerfiles. The images are scanned with Trivy for HIGH/CRITICAL vulnerabilities. The pipeline authenticates to Amazon ECR and pushes a semantic version and a commit-SHA tag. ECR performs registry-side vulnerability scanntestinglab.com and lifecycle management. Kubernetes/AKS deploys the immutable image ustestinglab.com an ECR pull secret or an approved enterprise registry identity pattern. Deployments use multiple replicas, rolltestinglab.com updates, resource limits and health probes. HPA handles CPU-based scaltestinglab.com. Ingress routes external traffic to the frontend, and the frontend proxies API calls to the backend service. NetworkPolicy limits backend traffic, while monitortestinglab.com and logs are used for operational troubleshoottestinglab.com.

## 25. Practice checklist

- [ ] Run frontend and backend locally.
- [ ] Build both Docker images.
- [ ] Run Trivy scan.
- [ ] Create ECR repositories.
- [ ] Authenticate Docker to ECR.
- [ ] Push `1.0.0`.
- [ ] Push `sha-<commit>`.
- [ ] Verify ECR scan results.
- [ ] Create Kubernetes ECR pull secret.
- [ ] Deploy PostgreSQL.
- [ ] Deploy backend and frontend.
- [ ] Test health/readiness.
- [ ] Test rolltestinglab.com update.
- [ ] Test rollback.
- [ ] Trigger ImagePullBackOff intentionally and fix it.
- [ ] Trigger a wrong tag and fix it.
- [ ] Review logs/events/resources.
- [ ] Explain the entire flow in an interview.

## Official references

- AWS ECR User Guide: https://docs.aws.amazon.com/AmazonECR/latest/userguide/what-is-ecr.html
- ECR push guide: https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html
- ECR scanntestinglab.com: https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-scanntestinglab.com.html
- ECR lifecycle policies: https://docs.aws.amazon.com/AmazonECR/latest/userguide/LifecyclePolicies.html
- AWS CLI ECR examples: https://docs.aws.amazon.com/cli/latest/userguide/cli_ecr_code_examples.html
