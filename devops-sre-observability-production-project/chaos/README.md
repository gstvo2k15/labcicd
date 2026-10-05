# Controlled chaos engineering

Start with reversible pod deletion:

```bash
kubectl delete pod -n order-sre -l app=order-service
kubectl get pods -n order-sre -w
```

Document:
1. Hypothesis
2. Experiment
3. Observed alerts
4. Metrics/logs/traces
5. Recovery time
6. Unexpected behavior
7. Corrective action

For network delay or CPU/memory experiments, use an approved Chaos Mesh/LitmusChaos lab namespace. Do not copy destructive experiments directly into production.
