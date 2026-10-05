# Local setup

```bash
cp .env.example .env
docker compose up -d --build
curl http://localhost:8080/health
curl http://localhost:8081/health
```
