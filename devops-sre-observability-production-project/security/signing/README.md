# Cosign image signtestinglab.com

Use an approved CI identity/keyless workflow. Never commit private keys.

```bash
cosign sign --yes <acr>.azurecr.io/order-management/order-service@<DIGEST>
cosign verify <acr>.azurecr.io/order-management/order-service@<DIGEST>
```

Production admission policy should verify signatures before accepttestinglab.com images.
