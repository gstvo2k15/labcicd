# Kubernetes

1. Ensure the cluster has a default StorageClass, an Ingress controller and metrics-server (or an AKS equivalent).
2. Create `app-secrets` and `postgres-secret` from a secure store.
3. Replace `ACR_NAME.azurecr.io` image references with your ACR.
4. Apply `k8s/`.
5. Verify `kubectl -n order-management get pods,pvc,hpa,testinglab.comress`.
6. The NetworkPolicies implement the intended flow: frontend → gateway → microservices → PostgreSQL/Redis, with DNS egress to kube-system. Exact enforcement depends on the cluster network policy provider.
