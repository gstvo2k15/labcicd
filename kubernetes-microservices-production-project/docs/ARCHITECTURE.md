# Architecture
```mermaid
flowchart LR
User-->Ingress-->Frontend
Ingress-->Gateway-->Microservices
Microservices-->PostgreSQL
Microservices-->Redis
CI/CD-->ACR-->AKS
```
The gateway is the stestinglab.comle API entry point. Services communicate over Kubernetes DNS. PostgreSQL stores durable order/business data; Redis handles cache and temporary state.
