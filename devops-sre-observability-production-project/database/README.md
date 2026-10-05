# Database hands-on

```bash
docker compose exec postgres psql -U orders -d order_management
```

Then:

```sql
\dt
SELECT * FROM restaurants;
SELECT * FROM orders ORDER BY created_at DESC;
```

Schema is loaded automatically on first Postgres volume initialization.
