# SLI / SLO

Practice targets:
- Availability: 99.9%
- Latency under 500ms: 99%
- Order creation success: 99.9%
- Payment success: 99.5%

Availability example:

```promql
1 - (
  sum(rate(http_requests_total{status=~"5.."}[5m]))
  /
  clamp_min(sum(rate(http_requests_total[5m])), 1)
)
```

Latency:

```promql
histogram_quantile(
  0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)
```

A 99.9% SLO permits a 0.1% failure fraction. Burn-rate alerting compares observed failure against the sustainable SLO failure rate.
