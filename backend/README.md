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

## Core API roots

- `/api/datasets/`
- `/api/metadata/field-types/`
- `/api/accounts/me/`
- `/api/organizations/`
