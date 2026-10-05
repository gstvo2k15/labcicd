# Disaster recovery
Back up PostgreSQL with `scripts/db-backup.sh`, store backups in durable encrypted storage, periodically test restore with `scripts/db-restore.sh`, retain immutable container image tags/digests, and use `kubectl rollout undo` for application rollback. Define RPO/RTO with the platform owner.
