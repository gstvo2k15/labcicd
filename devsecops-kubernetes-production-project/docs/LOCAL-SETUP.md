# Local setup
1. Install Docker Desktop, Git, Python 3.12 and Node 22.
2. Copy `.env.example` to `.env` and change local-only values.
3. Run `docker compose build && docker compose up -d`.
4. Open http://localhost:3000.
5. Register/login using the form. Restaurants come from the seed data.
6. Inspect logs with `docker compose logs -f api-gateway`.
