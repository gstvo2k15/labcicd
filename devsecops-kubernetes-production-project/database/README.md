# Database
Run `schema.sql` first, then `seed.sql`. The Compose stack mounts both files into `/docker-entrypoint-initdb.d/`, so a fresh PostgreSQL volume initializes automatically.
