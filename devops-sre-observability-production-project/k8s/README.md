# Kubernetes hands-on

For AKS, replace `REPLACE_ACR` and use immutable image tags/digests.

```bash
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml serviceaccounts.yaml rbac.yaml networkpolicies.yaml
kubectl apply -f postgres.yaml redis.yaml app.yaml hpa.yaml pdb.yaml ingress.yaml
kubectl get pods -n order-sre
```

For real production, move database credentials to Key Vault/Workload Identity and use a managed PostgreSQL service rather than the demo Postgres Deployment.
