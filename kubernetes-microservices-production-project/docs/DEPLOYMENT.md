# Deployment
1. Create Azure infrastructure with Terraform.
2. Get AKS credentials: `az aks get-credentials -g <rg> -n <aks>`.
3. Build/push images to ACR.
4. Replace `YOUR_ACR` in k8s manifests or use Helm values.
5. Create secrets from approved secret-management process.
6. `kubectl apply -k k8s/` or `kubectl apply -f k8s/`.
7. `kubectl -n food-delivery rollout status deployment/order-service`.
8. Configure DNS/TLS for the Ingress host.
