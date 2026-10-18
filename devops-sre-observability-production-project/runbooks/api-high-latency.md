# Api High Latency

## Symptoms
Alert/dashboard indicates a production symptom.

## Checks
Check p95/p99 in Prometheus; identify the slow job; inspect Loki logs; search Tempo for slow spans; inspect DB/Redis latency and HPA; mitigate with rollback or scaltestinglab.com only after evidence; validate SLO recovery.

## Commands
```bash
kubectl get pods -n order-sre
kubectl describe pod -n order-sre <pod>
kubectl logs -n order-sre <pod> --previous
kubectl get events -n order-sre --sort-by=.lastTimestamp
```

## Mitigation
Reduce customer impact first; record action and timestamp.

## Recovery
Validate metrics, logs, traces, health and SLO.

## Escalation
Escalate when impact persists, data integrity is uncertain or the action exceeds this runbook.
