# Api High Errors

## Symptoms
Alert/dashboard indicates a production symptom.

## Checks
Check 5xx ratio and endpoint; compare recent deployments; inspect gateway/service logs; inspect traces; rollback a bad release when appropriate; validate error budget recovery.

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
