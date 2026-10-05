# Trivy

```bash
docker build -t order-sre-order-service:local -f app/order-service/Dockerfile .
trivy image --severity HIGH,CRITICAL --exit-code 1 order-sre-order-service:local
trivy config k8s/
```
