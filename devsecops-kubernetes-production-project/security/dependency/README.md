# Dependency security
Python: `pip-audit -r requirements.txt`. Node: `npm audit --omit=dev --audit-level=high`. The CI pipeline treats high/critical findings as configurable failures.
