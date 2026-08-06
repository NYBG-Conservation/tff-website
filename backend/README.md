# Thain Family Forest Backend (Django)

## Quick start

Run these from the **repo root** unless noted.

1. Create and activate a virtualenv (macOS / Linux):

```bash
python3.12 -m venv .venv-local
source .venv-local/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv-local
.venv-local\Scripts\Activate.ps1
```

After activation, your shell prompt usually shows `(.venv-local)`. Use `deactivate` to exit the venv.

2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Copy env template:

```bash
cp backend/.env.example backend/.env   # macOS / Linux
# copy backend\.env.example backend\.env   # Windows
```

Set `USE_SQLITE=true` in `backend/.env` for local dev without Postgres.

4. Run migrations:

```bash
python backend/manage.py migrate
```

5. Create a superuser:

```bash
python backend/manage.py createsuperuser
```

6. (Optional) Seed research projects and sample files — **[docs/SEED_DATA.md](../docs/SEED_DATA.md)** (read before re-running seeds).

**NYBG operations:** [docs/NYBG_OPERATIONS_GUIDE.md](../docs/NYBG_OPERATIONS_GUIDE.md)

7. Run server:

```bash
python backend/manage.py runserver 0.0.0.0:8000
```

## Database mode (Postgres default, SQLite fallback)

- Default mode is Postgres (works with Docker/local Postgres later without any code changes).
- To run locally without Postgres, set `USE_SQLITE=true` in `backend/.env`, then run migrations/server as usual.

## Base apps

- `apps.accounts`: four platform roles — see [API_CONTRACT.md](API_CONTRACT.md#roles)
- `apps.organizations`: organizations and partners
- `apps.datasets`: dataset records, metadata definitions, metadata values, and file versions
- `apps.applications`: public Living Collections research applications + admin review queue

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
- `/api/public/research-applications/` (POST, anonymous)
- `/api/public/research-application-invites/claim/` (POST, anonymous invite claim)
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
