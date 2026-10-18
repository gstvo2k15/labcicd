# Deployment Runbook

1. Configure AWS CLI and verify `aws sts get-caller-identity`.
2. Create ECR repositories.
3. Build frontend/backend images.
4. Scan with Trivy.
5. Login to ECR.
6. Push semantic and SHA tags.
7. Verify ECR images/scans.
8. Configure Kubernetes namespace, DB secret and ECR pull secret.
9. Deploy PostgreSQL.
10. Deploy backend/frontend.
11. Verify rollout, services, endpoints, probes and HPA.
12. Apply Ingress if an Ingress controller is installed.
13. Test the application.
14. Promote a new SHA image ustestinglab.com a rolltestinglab.com update.
15. Roll back if health checks fail.
