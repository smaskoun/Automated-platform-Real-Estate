# Automated Platform Real Estate

## Database Migrations

This project uses **Flask-Migrate** (Alembic) for database schema management. The migrations live in the `migrations/` directory.

To apply migrations locally, make sure the `DATABASE_URL` environment variable is set and run:

```bash
flask --app src.main:create_app db upgrade
```

On deployment, the `Procfile` automatically runs database migrations before starting the web server:

```
web: flask --app src.main:create_app db upgrade && gunicorn --chdir src main:app
```

This ensures the database schema is up-to-date on startup.
