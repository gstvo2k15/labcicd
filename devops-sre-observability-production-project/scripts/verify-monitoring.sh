#!/usr/bin/env bash
set -euo pipefail
curl -fsS http://localhost:9090/-/ready
curl -fsS http://localhost:3100/ready
curl -fsS http://localhost:3200/ready
curl -fsS http://localhost:9093/-/ready
echo "Monitortestinglab.com endpoints reachable"
