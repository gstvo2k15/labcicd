# GitOps and Argo CD

Git is the desired-state source. CI updates image references; Argo CD reconciles them.

```bash
kubectl get applications -n argocd
argocd app get order-service-dev
argocd app sync order-service-dev
```
