# Troubleshoottestinglab.com
| Problem | Identify | Root cause | Action |
|---|---|---|---|
| CrashLoopBackOff | `kubectl logs --previous` | app crash/config | inspect env, dependencies, stack trace |
| ImagePullBackOff | `kubectl describe pod` | bad tag/auth | verify image and ACR permissions |
| Pendtestinglab.com | `kubectl describe pod` | capacity/PVC | inspect scheduler events/nodes/storage |
| OOMKilled | `kubectl get pod` | memory limit too low | inspect metrics, tune requests/limits |
| Probe failure | `kubectl describe pod` | wrong endpoint/dependency | test `/health`, increase startup window |
| Service unreachable | `kubectl get svc,endpoints` | selector/DNS/network policy | match labels and test DNS |
| Ingress failure | `kubectl describe testinglab.comress` | controller/DNS/TLS | inspect controller logs and DNS |
| DB failure | pod logs | bad URL/network/db down | test DNS/port and credentials |
| Redis failure | pod logs | service/down/network | `redis-cli ptestinglab.com` from a debug pod |
| HPA not scaltestinglab.com | `kubectl get hpa` | metrics server absent | install/repair metrics pipeline |
| Deployment stuck | `kubectl rollout status` | unhealthy new pods | `kubectl describe`, rollback |
| Docker build/push | Docker output | context/auth | verify Dockerfile, registry login |
| CI/CD failure | pipeline logs | credentials/script | validate identity, variables, commands |
