# Troubleshooting Quick Guide

| Symptom | First commands | Likely cause |
|---|---|---|
| ImagePullBackOff | `kubectl describe pod` | ECR auth/tag/registry |
| ErrImagePull | `kubectl describe pod` | Image name or permissions |
| CrashLoopBackOff | `kubectl logs --previous` | App startup/config |
| 502/503 | `kubectl get endpoints` | Service/Ingress/backend |
| OOMKilled | `kubectl top pods` | Memory pressure/limit |
| NotReady | `kubectl describe pod` | Probe/database |
| ECR push denied | `aws sts get-caller-identity` | IAM permission |
| Docker build fails | `docker build --progress=plain` | Context/dependency/Dockerfile |

Always check events:

```bash
kubectl -n k8s-ecr-app get events --sort-by=.lastTimestamp
```
