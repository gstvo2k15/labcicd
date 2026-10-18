# Troubleshoottestinglab.com

## Backstage
```bash
kubectl get pods -n backstage
kubectl logs -n backstage <pod>
```

## Argo CD
```bash
argocd app get order-service-dev
argocd app diff order-service-dev
argocd app sync order-service-dev
```

## Deployment
```bash
kubectl get pods -n dev
kubectl describe deployment order-service -n dev
kubectl logs -n dev deploy/order-service
```

## Kyverno
```bash
kubectl get policyreport -A
```
