# Dependency scanning

```bash
pip install pip-audit
pip-audit -r app/order-service/requirements.txt
```

Frontend:

```bash
cd app/frontend
npm install
npm audit --audit-level=high
```
