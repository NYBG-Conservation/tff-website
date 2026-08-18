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

**Current hosting:** Django API + admin run on **AWS EC2** (Docker Compose). SSH into the instance to deploy and run management commands. The public SvelteKit site is on **Vercel** and reads the Django public API. Uploads live on the EC2 `media_data` volume (S3 is not in use yet). Staging currently serves the API at `http://<EC2_IP>:8000` with `USE_HTTPS=false` — do not use that setup for a public launch. Full runbook: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

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

### Production / staging (current)

| Layer | Where it runs now |
|-------|-------------------|
| Public frontend | Vercel (SvelteKit). Set `PUBLIC_DJANGO_API_BASE_URL` to the Django origin. |
| API + admin | AWS EC2, Docker service **`backend`** (`docker-compose.prod.yml`) |
| Database | RDS Postgres in production; SQLite or local Docker Postgres on a laptop |
| Uploads | `backend/media/` on the EC2 `media_data` volume |

SSH to the instance (security group: port 22 from your IP), then from the clone (`~/tff-website`):

```bash
ssh -i /path/to/key.pem <user>@<EC2_PUBLIC_IP>
cd ~/tff-website
git pull
docker compose -f docker-compose.prod.yml up --build -d
docker compose -f docker-compose.prod.yml exec backend python backend/manage.py migrate
```

Django is **not** installed on the Ubuntu host — always `exec` into the `backend` container. Copy `backend/.env.production.example` → `backend/.env` on the server (RDS URL, `DJANGO_SECRET_KEY`, hosts, CORS/CSRF). Prefer an EC2 IAM role for AWS access instead of long-lived keys.

**Still later:** grant-isolated AWS Organizations member account, S3 for uploads at scale, and public HTTPS (ALB / `USE_HTTPS=true`, no open port 8000). See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

---

## In this repository

You’ll find:

### Architecture

Public **SvelteKit** site plus a **Django + Postgres** API in `backend/`. The frontend calls `/api/...` (auth, datasets, public research/data pages).

```
Browser  →  Vercel (SvelteKit)
         →  EC2 Docker / Gunicorn (Django admin + API)
                →  RDS (metadata, users, datasets)
                →  EC2 volume (uploaded files; S3 later)
```

Local laptops still use SQLite or Docker Postgres. Diagram and account layout: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#architecture).

### Connecting to deployment (Vercel / AWS SSH)

- **Local:** two terminals — Django on `127.0.0.1:8000`, frontend via `npm run dev`. See [Active development](#active-development-now). Docker alternative: `docker compose up` ([backend/README.md](backend/README.md)).
- **Vercel:** public SvelteKit site. Set `PUBLIC_DJANGO_API_BASE_URL` to the Django origin. Vercel does not run Django or talk to RDS.
- **EC2 (active):** SSH with the instance `.pem` (port 22 from your IP). Deploy with `docker compose -f docker-compose.prod.yml`. RDS (when used) is reachable only from the EC2 security group. Secrets live in `backend/.env` on the host — see [Production / staging (current)](#production--staging-current).

Full runbook: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md). Staff ops: [docs/NYBG_OPERATIONS_GUIDE.md](docs/NYBG_OPERATIONS_GUIDE.md).

### Data cleaning / management pipeline

Researchers create and validate datasets in Django admin (roles, required fields, Figshare, upload policy — [docs/EXTERNAL_PARTNER_GUIDE.md](docs/EXTERNAL_PARTNER_GUIDE.md)). Postgres stores users, organizations, dataset metadata, and file-version pointers. Binaries go to `backend/media/` locally or on the EC2 volume; S3 is planned for production-scale uploads. Public `/research` and `/data` pages only show records marked `shared_publicly` / `expose_on_public_api`. Seed/cleanup workflows: [docs/SEED_DATA.md](docs/SEED_DATA.md). Sample binaries under `src/lib/data/tff-sample-data/` are for import scripts, not the Vercel bundle.
