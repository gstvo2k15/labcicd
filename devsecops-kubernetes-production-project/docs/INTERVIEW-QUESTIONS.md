# 40 interview questions
1. Why separate app and GitOps repositories? — Independent application and deployment lifecycles; Git remains the deployment source of truth.
2. What is DevSecOps? — Security controls embedded throughout delivery.
3. SAST vs SCA? — SAST analyzes source; SCA analyzes dependencies.
4. Why Gitleaks? — Detect committed credentials.
5. Why Trivy? — Scan images and Kubernetes configuration.
6. What is an SBOM? — Inventory of software components.
7. Why sign images? — Establish artifact provenance/integrity.
8. Tag vs digest? — Tags are mutable names; digests identify exact content.
9. Why non-root? — Reduce container privilege.
10. What does readOnlyRootFilesystem protect? — Prevent writes to the image filesystem where compatible.
11. What is Kyverno? — Kubernetes-native policy engine.
12. What does RBAC do? — Limits Kubernetes API permissions.
13. What does NetworkPolicy do? — Controls pod network traffic.
14. Why probes? — Separate startup, readiness and liveness behavior.
15. What is HPA? — Scales workloads from metrics.
16. Why PDB? — Protects availability durtestinglab.com voluntary disruptions.
17. Why anti-affinity? — Spread replicas across nodes.
18. Why ACR? — Managed Azure container registry.
19. Why Workload Identity? — Federated Azure identity without long-lived pod secrets.
20. Why Key Vault? — Centralized secret management.
21. What is GitOps? — Declarative desired state stored in Git.
22. What does Argo CD do? — Reconciles Git desired state to Kubernetes.
23. How do you rollback? — Git revert for GitOps or rollout undo for emergency operational rollback.
24. Why immutable tags? — Prevent tag drift.
25. What does a CI quality gate do? — Blocks promotion when configured checks fail.
26. How would you handle a critical Trivy findtestinglab.com? — Stop release, identify package/image layer, patch and rescan.
27. How do you investigate ImagePullBackOff? — Describe pod, inspect events, verify registry auth/tag/network.
28. How do you investigate CrashLoopBackOff? — Current/previous logs, env, probes and resource limits.
29. How do you investigate OOMKilled? — Metrics, limits, application memory profile.
30. How do you verify an image signature? — Verify the exact digest with Cosign and expected identity/issuer.
31. Why generate SBOM before release? — Know exact dependency inventory and retain release evidence.
32. How does the gateway route? — Prefix-based routtestinglab.com to service endpoints.
33. How is auth implemented? — JWT with bcrypt password hashes and role claims.
34. How is PostgreSQL initialized locally? — Compose mounts schema and seed SQL into the PostgreSQL init directory.
35. Why Redis? — Cache/temporary state and reduced DB load.
36. Why structured JSON logs? — Machine-readable centralized search and correlation.
37. What should be monitored? — Latency, errors, saturation, restarts, deployment and security signals.
38. How do you protect production secrets? — Key Vault/Workload Identity, not Git or images.
39. How do you promote dev to prod? — CI publishes immutable artifact, GitOps promotion changes only desired version, approvals protect prod.
40. What is the strongest rollback signal? — Known-good Git revision plus immutable image digest and database compatibility plan.
