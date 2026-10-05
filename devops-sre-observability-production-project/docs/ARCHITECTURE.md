# ARCHITECTURE

Application traffic goes through the gateway to microservices. OpenTelemetry exports telemetry to the Collector, which routes traces to Tempo and metrics/logs through the configured observability stack.
