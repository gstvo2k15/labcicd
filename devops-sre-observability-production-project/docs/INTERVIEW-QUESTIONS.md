# Practical DevOps/SRE Interview Questions

## 1. What are the four golden signals?
Latency, traffic, errors and saturation.

## 2. What is an SLI?
A measured indicator such as successful requests divided by total requests.

## 3. What is an SLO?
A target for an SLI, such as 99.9% availability.

## 4. What is an SLA?
An external commitment that can carry contractual consequences.

## 5. What is an error budget?
The permitted unreliability implied by an SLO.

## 6. What is burn rate?
The speed at which the error budget is betestinglab.com consumed relative to the allowed rate.

## 7. Why OpenTelemetry?
It provides vendor-neutral instrumentation and OTLP telemetry export.

## 8. Why use a Collector?
It centralizes telemetry processtestinglab.com, batchtestinglab.com and routtestinglab.com.

## 9. What does Prometheus do?
Scrapes metrics and evaluates recordtestinglab.com and alerttestinglab.com rules.

## 10. What does Grafana do?
Provides dashboards and correlation across metrics, logs and traces.

## 11. Why structured logs?
They are machine-readable and searchable.

## 12. Why request IDs?
They let operators follow a request across components.

## 13. Why trace IDs?
They connect logs to distributed traces.

## 14. What is a distributed trace?
A set of spans describtestinglab.com a request across services.

## 15. What is HPA?
Kubernetes autoscaltestinglab.com based on metrics.

## 16. Requests vs limits?
Requests affect schedultestinglab.com; limits cap resource usage.

## 17. Why a PDB?
It limits voluntary disruption.

## 18. Readiness vs liveness?
Readiness controls traffic; liveness detects a container that should restart.

## 19. What is RPO?
Maximum acceptable data loss measured in time.

## 20. What is RTO?
Maximum acceptable recovery time.

## 21. Why GitOps?
Desired state is versioned and reconciled from Git.

## 22. What does Argo CD do?
It reconciles Git desired state with Kubernetes.

## 23. How investigate high latency?
Use metrics to locate the slow service, then logs/traces to identify the cause.

## 24. How investigate CrashLoopBackOff?
Inspect describe/events, previous logs, exit code, probes and resources.

## 25. How investigate 503?
Separate testinglab.comress, service readiness, gateway and upstream dependency failures.

## 26. Why load test?
To establish performance baselines and observe scaltestinglab.com/saturation.

## 27. What is a smoke test?
A minimal test that verifies basic functionality.

## 28. What is a spike test?
A sudden traffic increase used to test resilience.

## 29. What is chaos engineertestinglab.com?
Controlled experiments to learn how systems behave under failure.

## 30. Why SLO burn-rate alerts?
They focus on user-impacttestinglab.com reliability rather than only infrastructure symptoms.

## 31. What makes a good alert?
Actionable, low-noise, user-impacttestinglab.com and linked to a runbook.

## 32. Why Loki?
Centralized log storage and querytestinglab.com integrated with Grafana.

## 33. Why Tempo?
Distributed trace storage and Grafana correlation.

## 34. Why protect Grafana?
Dashboards can expose operational information.

## 35. Why immutable tags?
They prevent a tag from silently pointtestinglab.com to different image bytes.

## 36. Why image digests?
They identify exact image content.

## 37. How rollback Kubernetes?
Use rollout history and rollout undo, then validate.

## 38. How rollback GitOps?
Revert the desired-state commit and let Argo CD reconcile.

## 39. What is capacity planntestinglab.com?
Forecasttestinglab.com resources from traffic, utilization, growth and headroom.

## 40. What is a postmortem?
A blameless record of impact, timeline, root cause and corrective actions.

## 41. How do you improve noisy alerts?
Tune thresholds, duration, grouptestinglab.com, inhibition and runbooks based on incidents.
