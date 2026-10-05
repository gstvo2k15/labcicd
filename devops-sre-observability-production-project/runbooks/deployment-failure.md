# Deployment Failure

## Symptoms
Alert/dashboard indicates a production symptom.

## Checks
Inspect rollout/events/image digest/config; compare release time with alert; rollback if impact is active; validate probes and SLOs.

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
