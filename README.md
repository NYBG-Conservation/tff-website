# Thain Family Forest Website + Database

Annie Fu (afu@nybg.org)

### Development began January 2026

## Active development (now)


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
| http://127.0.0.1:8000/admin/ | Django admin (primary management UI) |
| http://localhost:5173/projects | Redirects to Django admin |

**Minimal `backend/.env` for SQLite:**

```bash
USE_SQLITE=true
DJANGO_SECRET_KEY=dev-only-change-me
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174
```

Optional: `createsuperuser` + seed commands — see [docs/SEED_DATA.md](docs/SEED_DATA.md).

**NYBG staff handoff:** see **[docs/NYBG_OPERATIONS_GUIDE.md](docs/NYBG_OPERATIONS_GUIDE.md)** for the full operations runbook (admin, roles, public content, seeds, troubleshooting).

**External partners:** see **[docs/EXTERNAL_PARTNER_GUIDE.md](docs/EXTERNAL_PARTNER_GUIDE.md)** (account setup, required fields, Figshare, upload policy).

**Docker alternative:** `docker compose up` (local Postgres + Django) — see [backend/README.md](backend/README.md).

Production AWS (Vercel, EC2, RDS, member account) is documented in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for when you are ready.

---

## Backend

A Django + Postgres backend scaffold now lives in `backend/` for researcher/admin dataset workflows.

- Setup guide: `backend/README.md`
- API contract: `backend/API_CONTRACT.md`

### Public research/data pages

The `/research` and `/data` routes load from the Django public API (`/api/public/projects/`, `/api/public/datasets/`). Set `PUBLIC_DJANGO_API_BASE_URL` in a root `.env` file (see `.env.example`) and mark records `shared_publicly` / `expose_on_public_api` in Django admin.

**Operations guide:** [docs/NYBG_OPERATIONS_GUIDE.md](docs/NYBG_OPERATIONS_GUIDE.md)

### Public API + sample data

See [docs/SEED_DATA.md](docs/SEED_DATA.md) for safe seed/cleanup workflows (avoid duplicate projects).

### Minimal architecture

The Svelte frontend calls Django REST endpoints under `/api/...`. Django handles auth, permissions, and dataset validation, and Postgres stores users, organizations, datasets, metadata definitions/values, and file version records.

### Production deployment (later)

Deferred until a dedicated AWS member account email is available. When ready:

- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — Vercel, EC2, RDS, S3, grant billing, sample-data storage

---

## In this repository

You’ll find:

### Architecture

Public **SvelteKit** site plus a **Django + Postgres** API in `backend/`. The frontend calls `/api/...` (auth, datasets, public research/data pages). Production target: Vercel (frontend) → EC2/Docker Gunicorn (Django) → RDS (metadata) → S3 (uploads), in a grant-isolated AWS member account. That AWS track is **deferred**; local work uses SQLite or Docker Postgres.

Diagram and account layout: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#architecture).

### Connecting to deployment (Vercel / AWS SSH)

- **Local (active now):** two terminals — Django on `127.0.0.1:8000`, frontend via `npm run dev`. See [Active development](#active-development-now). Docker alternative: `docker compose up` ([backend/README.md](backend/README.md)).
- **Vercel (planned):** deploy the SvelteKit app; set `PUBLIC_DJANGO_API_BASE_URL` to the Django HTTPS origin. Vercel does not run Django or talk to RDS.
- **EC2 (planned):** SSH to the instance (security group: port 22 from your IP only), then `docker compose -f docker-compose.prod.yml up --build -d`. RDS is reachable only from the EC2 security group.

Full runbook: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md). Staff ops: [docs/NYBG_OPERATIONS_GUIDE.md](docs/NYBG_OPERATIONS_GUIDE.md).

### Data cleaning / management pipeline

Researchers create and validate datasets in Django admin (roles, required fields, Figshare, upload policy — [docs/EXTERNAL_PARTNER_GUIDE.md](docs/EXTERNAL_PARTNER_GUIDE.md)). Postgres stores users, organizations, dataset metadata, and file-version pointers; binaries go to disk locally or S3 in production. Public `/research` and `/data` pages only show records marked `shared_publicly` / `expose_on_public_api`. Seed/cleanup workflows: [docs/SEED_DATA.md](docs/SEED_DATA.md). Sample binaries under `src/lib/data/tff-sample-data/` are for import scripts, not the Vercel bundle.
