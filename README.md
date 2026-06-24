# Thain Family Forest Website + Database

Annie Fu (afu@nybg.org)

### Development began January 2026

## Active development (now)

AWS Organizations and a separate grant member account are **on hold** until you have a unique root email. Use local development in the meantime.

**Terminal 1 — API (Python 3.10+):**

```bash
python3.12 -m venv .venv-local
source .venv-local/bin/activate
pip install -r backend/requirements.txt

cp .env.example .env
# backend/.env: USE_SQLITE=true (see example below)

python backend/manage.py migrate
python backend/manage.py runserver 127.0.0.1:8000
```

**Terminal 2 — frontend:**

```bash
npm install
npm run dev
```

| URL | Purpose |
|-----|---------|
| http://localhost:5173 (or 5174) | Public site |
| http://127.0.0.1:8000/admin/ | Django admin |
| http://localhost:5173/projects | Researcher project dashboard (needs login) |

**Minimal `backend/.env` for SQLite:**

```bash
USE_SQLITE=true
DJANGO_SECRET_KEY=dev-only-change-me
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174
```

Optional: `createsuperuser` + seed commands — see [docs/SEED_DATA.md](docs/SEED_DATA.md).

**Docker alternative:** `docker compose up` (local Postgres + Django) — see [backend/README.md](backend/README.md).

Production AWS (Vercel, EC2, RDS, member account) is documented in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for when you are ready.

---

## Backend

A Django + Postgres backend scaffold now lives in `backend/` for researcher/admin dataset workflows.

- Setup guide: `backend/README.md`
- API contract: `backend/API_CONTRACT.md`

### Public research/data pages

The `/research` and `/data` routes load from the Django public API (`/api/public/projects/`, `/api/public/datasets/`). Set `PUBLIC_DJANGO_API_BASE_URL` in a root `.env` file (see `.env.example`) and mark records `shared_publicly` / `expose_on_public_api` in the admin or `/projects` dashboard.

### Public API + sample data

See [docs/SEED_DATA.md](docs/SEED_DATA.md) for safe seed/cleanup workflows (avoid duplicate projects).

### Minimal architecture

The Svelte frontend calls Django REST endpoints under `/api/...`. Django handles auth, permissions, and dataset validation, and Postgres stores users, organizations, datasets, metadata definitions/values, and file version records.

### Production deployment (later)

Deferred until a dedicated AWS member account email is available. When ready:

- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — Vercel, EC2, RDS, S3, grant billing, sample-data storage