# Thain Family Forest Backend (Django)

## Quick start

1. Create and activate a virtualenv.
2. Install dependencies:
   - `pip install -r backend/requirements.txt`
3. Copy env template:
   - `copy backend\\.env.example backend\\.env` (Windows)
4. Run migrations:
   - `python backend/manage.py migrate`
5. Create a superuser:
   - `python backend/manage.py createsuperuser`
6. Run server:
   - `python backend/manage.py runserver 0.0.0.0:8000`

## Database mode (Postgres default, SQLite fallback)

- Default mode is Postgres (works with Docker/local Postgres later without any code changes).
- To run locally without Postgres, set `USE_SQLITE=true` in `backend/.env`, then run migrations/server as usual.

## Base apps

- `apps.accounts`: user roles (`internal_admin`, `external_partner_admin`)
- `apps.organizations`: organizations and partners
- `apps.datasets`: dataset records, metadata definitions, metadata values, and file versions

## Apply database migrations

After pulling model changes:

```bash
python backend/manage.py migrate
```

Latest migration (`0005`) adds:

- `Project.slug` — stable public identifier (backfilled from existing titles)
- `ProjectAlert` — tracks overdue missing-data alerts (see `OVERDUE_DATA_ALERT_SPEC.md`)
- `DatasetFile.external_url` — optional external asset link when files are hosted elsewhere

## Core API roots

- `/api/datasets/`
- `/api/metadata/field-types/`
- `/api/accounts/me/`
- `/api/organizations/`

## Docker Compose (Django + Postgres)

From repo root:

1. Build and start services:
   - `docker compose up --build -d`
2. Run migrations inside the backend container:
   - `docker compose exec backend python backend/manage.py migrate`
3. Create a superuser:
   - `docker compose exec backend python backend/manage.py createsuperuser`
4. View logs:
   - `docker compose logs -f backend`

Service URLs:
- Backend API: `http://localhost:8000`
- Postgres: `localhost:5432` (`postgres/postgres`, db `tff_db`)

Stop services:
- `docker compose down`

Stop and remove DB volume (fresh database reset):
- `docker compose down -v`
