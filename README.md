# Automated Platform Real Estate

## Environment variables

Create a `.env` file in the project root (or configure the variables in your
hosting provider) with the following keys before running the backend or any of
the scraper utilities:

| Variable | Required | Description |
| --- | --- | --- |
| `APIFY_API_KEY` | When using Apify-hosted scrapers | API token used by the Apify client to trigger actors and datasets. |
| `GOOGLE_MAPS_API_KEY` | When rendering Google Maps features | Maps API key used by the frontend to request geocoding, tiles, or place details. |

Optional scraper settings allow you to fine-tune how local scraping runs:

| Variable | Purpose |
| --- | --- |
| `SCRAPER_PROVIDER` | Select which scraping runtime to use (`apify`, `puppeteer`, or `playwright`). |
| `SCRAPER_HEADLESS` | Set to `false` to watch browser automation run locally; defaults to headless mode. |
| `PUPPETEER_EXECUTABLE_PATH` | Override the Chromium/Chrome binary Puppeteer should launch. |
| `PLAYWRIGHT_BROWSERS_PATH` | Reuse an existing Playwright browser download (especially helpful in CI). |

## Database Migrations

This project uses **Flask-Migrate** (Alembic) for database schema management. The migrations live in the `migrations/` directory.

To apply migrations locally, make sure the `DATABASE_URL` environment variable is set and run:

```bash
flask --app src.main:create_app db upgrade
```

On deployment, the `Procfile` automatically runs database migrations before starting the web server:

```
web: flask --app src.main:create_app db upgrade && gunicorn src.main:app
```

Make sure this command runs from the project root so the `src` package is
available on `PYTHONPATH`. If you need to run it from elsewhere, set
`PYTHONPATH` to include the project root.

This ensures the database schema is up-to-date on startup.

## Startup checks

When the application starts it verifies that the critical tables
`brand_voices`, `social_media_accounts` and `social_media_posts` exist.
If any of these tables are missing, a clear error is logged and the
service exits instead of running against an incomplete schema.
