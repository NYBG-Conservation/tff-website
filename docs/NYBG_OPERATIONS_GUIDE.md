# NYBG Operations Guide — Thain Family Forest Website

**Audience:** NYBG staff taking over day-to-day management of the public website, research directory, dataset catalog, and Django admin backend.

**Last updated:** July 2026

This is the **primary handoff document**. It ties together local development, content management, user accounts, seed data, and production deployment. For deep dives, see the linked runbooks at the end.

---

## Table of contents

1. [What this system is](#1-what-this-system-is)
2. [Architecture at a glance](#2-architecture-at-a-glance)
3. [Repository layout](#3-repository-layout)
4. [Local development (daily workflow)](#4-local-development-daily-workflow)
5. [Environment variables](#5-environment-variables)
6. [User accounts and permissions](#6-user-accounts-and-permissions)
7. [Managing content in Django admin](#7-managing-content-in-django-admin)
8. [Public website pages](#8-public-website-pages)
9. [Making research and data visible to the public](#9-making-research-and-data-visible-to-the-public)
10. [Seed data and sample files](#10-seed-data-and-sample-files)
11. [Public API reference (what the site reads)](#11-public-api-reference-what-the-site-reads)
12. [Static site content (CSV files)](#12-static-site-content-csv-files)
13. [Production deployment](#13-production-deployment)
14. [Common tasks (cheat sheet)](#14-common-tasks-cheat-sheet)
15. [Troubleshooting](#15-troubleshooting)
16. [Related documentation](#16-related-documentation)

---

## 1. What this system is

The **Thain Family Forest (TFF) website** is a SvelteKit public site backed by a **Django REST API** and **PostgreSQL** (SQLite locally). It serves:

- A public-facing forest hub (home, about, visit, education, contact)
- A **research project directory** (`/research`) with project detail modals and publications
- A **data & archives catalog** (`/data`) with filterable datasets, expandable metadata, and public file downloads (desktop only)
- **Django admin** at `/admin/` for NYBG staff to manage projects, datasets, files, and publications

Researchers manage records through **Django admin** (not a separate custom dashboard — `/projects` redirects to admin).

| Layer | Technology | Where it runs |
|-------|------------|---------------|
| Public frontend | SvelteKit (Vite) | Vercel (production) or `localhost:5173` (local) |
| API + admin | Django 5 + DRF | EC2 Docker (production) or `127.0.0.1:8000` (local) |
| Database | PostgreSQL / SQLite | RDS (production) or `backend/db.sqlite3` (local) |
| Uploaded files | Filesystem (`backend/media/`) | EC2 volume today; S3 planned |

**Important:** The public site does **not** embed content in the frontend repo for research/data. Those pages load live from the Django **public API**. If Django is down or records are not published, `/research` and `/data` will show errors or empty lists.

---

## 2. Architecture at a glance

```mermaid
flowchart TB
  subgraph public [Public visitors]
    browser[Browser]
  end
  subgraph vercel [Vercel - SvelteKit]
    pages["/, /research, /data, ..."]
  end
  subgraph ec2 [EC2 - Django]
    admin["/admin/"]
    api["/api/public/*"]
    private["/api/projects, /api/datasets"]
  end
  subgraph db [(PostgreSQL / SQLite)]
    data[(Projects, Datasets, Users)]
  end

  browser --> pages
  pages -->|"PUBLIC_DJANGO_API_BASE_URL"| api
  browser --> admin
  admin --> data
  api --> data
  private --> data
```

**Content flow:**

1. Staff edits **Projects**, **Datasets**, and **Files** in Django admin.
2. Staff sets **Shared publicly** / **Expose on public API** flags (see [§9](#9-making-research-and-data-visible-to-the-public)).
3. SvelteKit server loads `/api/public/projects/`, `/api/public/datasets/`, `/api/public/publications/` on each page request.
4. Visitors see updated content after deploy is unnecessary for API-driven pages — only Django data changes matter.

---

## 3. Repository layout

```
tff-website/
├── src/                          # SvelteKit frontend
│   ├── routes/                   # Pages (+page.svelte, +page.server.ts)
│   │   ├── +page.svelte          # Home (research highlights)
│   │   ├── research/             # Research directory + conducting research
│   │   ├── data/                 # Data & archives table
│   │   └── projects/             # Redirects → Django admin
│   ├── lib/
│   │   ├── api/                  # API client helpers
│   │   ├── components/           # Nav, cards, hero, etc.
│   │   └── data/                 # Legacy static data + sample file folders
│   └── styles/all.css            # Global styles, link rules, scroll-padding
├── static/                       # Served as-is (events.csv, announcements.csv)
├── backend/
│   ├── apps/
│   │   ├── accounts/             # Users, roles, profiles
│   │   ├── organizations/
│   │   └── datasets/             # Projects, datasets, files, publications
│   ├── manage.py
│   └── db.sqlite3                # Local DB (gitignored in practice)
├── docs/
│   ├── NYBG_OPERATIONS_GUIDE.md  # ← this file
│   ├── SEED_DATA.md              # Seed commands runbook
│   └── DEPLOYMENT.md             # AWS / Vercel / EC2
├── .env                          # Frontend: PUBLIC_DJANGO_API_BASE_URL
└── backend/.env                  # Django: DB, CORS, CSRF, secrets
```

**Key backend models:**

| Model | Purpose |
|-------|---------|
| `Project` | Research project card (title, summary, description, slug, ongoing, partners) |
| `Dataset` | Data release linked to a project (cadence, status, data type) |
| `DatasetFile` | Uploaded file or external URL attached to a dataset |
| `MetadataFieldDefinition` | Schema fields for a dataset |
| `ProjectPublication` | Citation shown on `/research` |
| `Organization` | NYBG, partners, etc. |
| `User` + `UserProfile` | Login + platform role |

---

## 4. Local development (daily workflow)

You need **two terminals**: Django API and SvelteKit frontend.

### One-time setup

```bash
# From repo root
python3.12 -m venv .venv-local
source .venv-local/bin/activate          # NOT: python3 activate
pip install -r backend/requirements.txt

cp .env.example .env                     # frontend API URL
# Create backend/.env — see §5

python backend/manage.py migrate
python backend/manage.py createsuperuser
```

Optional sample data: [§10](#10-seed-data-and-sample-files) or [SEED_DATA.md](SEED_DATA.md).

### Every day

**Terminal 1 — API:**

```bash
cd /path/to/tff-website
source .venv-local/bin/activate
python backend/manage.py runserver 127.0.0.1:8000
```

**Terminal 2 — frontend:**

```bash
cd /path/to/tff-website
npm install    # first time only
npm run dev
```

### URLs (local)

| URL | Purpose |
|-----|---------|
| http://localhost:5173 | Public site |
| http://127.0.0.1:8000/admin/ | **Django admin (primary management UI)** |
| http://127.0.0.1:8000/api/public/projects/ | Public API (JSON) |

If `/research` or `/data` show “temporarily unavailable”, Django is probably not running or `PUBLIC_DJANGO_API_BASE_URL` in root `.env` is wrong.

### Activate the virtualenv correctly

The `activate` script is a **shell** script:

```bash
source .venv-local/bin/activate
```

Do **not** run `python3 .venv-local/bin/activate` — that causes a `SyntaxError`.

Alternative without activating:

```bash
.venv-local/bin/python backend/manage.py <command>
```

---

## 5. Environment variables

### Root `.env` (SvelteKit / Vercel)

| Variable | Purpose |
|----------|---------|
| `PUBLIC_DJANGO_API_BASE_URL` | Django API base URL, e.g. `http://127.0.0.1:8000` locally |

Used by server-side loaders on `/research`, `/data`, and the home page (indirectly).

### `backend/.env` (Django)

| Variable | Local example | Purpose |
|----------|---------------|---------|
| `USE_SQLITE` | `true` | Use `backend/db.sqlite3` instead of Postgres |
| `DJANGO_SECRET_KEY` | long random string | Session/crypto secret |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Host header allowlist |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173,...` | Browser origins for API |
| `CSRF_TRUSTED_ORIGINS` | same as CORS | CSRF for admin + API |
| `FRONTEND_URL` | `http://127.0.0.1:5173` | Root URL redirect target |

Production adds RDS, `USE_HTTPS=true`, S3, etc. — see [DEPLOYMENT.md](DEPLOYMENT.md).

---

## 6. User accounts and permissions

There are **two separate concepts**:

| Concept | What it controls | How to set |
|---------|------------------|------------|
| **Django `User`** (`is_staff`, `is_superuser`) | Can log into `/admin/` | `createsuperuser` |
| **`UserProfile.role`** | Which projects/datasets you see and edit in admin + API | `assign_internal_superadmin` or admin / API |

### Platform roles

| Role | Typical use | View scope | Edit scope |
|------|-------------|------------|------------|
| `internal_superadmin` | Platform owner | Everything | Everything; can assign roles |
| `internal_admin` | NYBG team admin | NYBG organization records | NYBG organization records |
| `external_superadmin` | Partner org lead | Their organization | Their organization |
| `external_admin` | External researcher | Owned + managed projects | Owned + managed projects |

Full API matrix: [backend/API_CONTRACT.md](../backend/API_CONTRACT.md).

### Create a shared NYBG team admin account

```bash
source .venv-local/bin/activate
python backend/manage.py createsuperuser
# username: e.g. nybg-admin
```

Set NYBG-scoped role:

```bash
python backend/manage.py shell
```

```python
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile

user = User.objects.get(username="nybg-admin")
user.profile.role = UserProfile.Role.INTERNAL_ADMIN
user.profile.organization = None
user.profile.save()
```

For **full platform access** (all orgs + assign roles):

```bash
python backend/manage.py assign_internal_superadmin nybg-admin
```

### Reset a forgotten password

```bash
source .venv-local/bin/activate
python backend/manage.py changepassword <username>
```

Log in at `/admin/` with **username** (not email).

### Promote an existing user (when logged in as superadmin)

```http
POST /api/accounts/assign-role/
Content-Type: application/json

{
  "username": "colleague",
  "role": "internal_admin"
}
```

Internal roles must **not** include `organization`. External roles require an organization id.

---

## 7. Managing content in Django admin

**URL:** `http://127.0.0.1:8000/admin/` (local) or `https://api.<your-domain>/admin/` (production)

### Projects

Path: **Datasets → Projects**

| Field | Public impact |
|-------|----------------|
| Short title | Card title on `/research` |
| Summary | Card subtitle |
| Description | Modal paragraphs (`\n\n` = new paragraph) |
| Slug | URL key (`/research?project=<slug>`, `/data?project=<slug>`) — read-only in API |
| **Shared publicly** | **Must be checked** for project to appear on `/research` |
| Ongoing | Green “Ongoing” vs gray “Concluded” tag |
| Institutional partners | Shown in project modal |
| Lead name / email | Shown in project modal |
| Organization | Scoping + metadata |
| **Figshare item URL / reserved DOI** | **Required for new projects** — data deposit on Figshare ([how to reserve a DOI](https://info.figshare.com/user-guide/how-to-reserve-a-doi/)) |

**Inlines on project:** Publications, Managers, Alerts.

When a concluded project passes its end date by 30 days with no linked dataset files, the system emails the project lead with upload instructions (`python backend/manage.py check_overdue_project_uploads` — schedule daily in production). See [OVERDUE_DATA_ALERT_SPEC.md](../backend/OVERDUE_DATA_ALERT_SPEC.md).

### Datasets

Path: **Datasets → Datasets**

| Field | Public impact |
|-------|----------------|
| Title | Row title on `/data` |
| Description | Expanded row detail |
| Project | Links dataset to research project |
| Cadence / Status / Data type | Filters and detail panel |
| **Expose on public API** | **Must be checked** for `/data` listing |
| Status | Only `active` and `archived` appear publicly (not `draft`) |

**Inlines:** Metadata fields, metadata values, files, publications.

### Dataset files

Each file can be:

- **Uploaded file** (stored under `backend/media/`), or
- **External URL** (required for files > 1 GB per governance policy)

| Field | Public impact |
|-------|----------------|
| **Expose on public API** | Listed on `/data` expanded row |
| File name | Shown as file type label + filename |
| File kind | Documentation, primary data, etc. |

Public download URL: `/api/public/datasets/<dataset_id>/files/<file_id>/download/`

Mobile browsers: download links are hidden on phones (large files); desktop only.

### Project publications

Path: **Datasets → Project publications** (or inline on project)

| Field | Public impact |
|-------|----------------|
| Citation | Text on `/research` |
| Featured | “Selected publications” highlight section |
| **Expose on public API** | Visible on public site |
| Project | Optional; blank = site-wide publication |

### From the public `/data` page

Each expanded dataset has **Manage dataset entry →** linking directly to that dataset’s admin change page. Sign-in note appears only when the visitor is not authenticated.

---

## 8. Public website pages

| Route | Data source | Notes |
|-------|-------------|-------|
| `/` | Static + `announcements.csv` hero image | Research highlights cards → `/research?project=` |
| `/about`, `/visit`, `/education`, `/contact` | Mostly static Svelte content | Education is placeholder |
| `/research` | Public API | 3 sections: overview, conducting research, project directory + publications |
| `/data` | Public API | Filterable/sortable table; expandable rows |
| `/projects` | Redirect | → Django admin (project search if `?project=` set) |
| `/blue-zones` | Separate map app | Custom layout |

### `/research` structure

1. **Overview** — static intro copy
2. **Conducting research** — application button (Survey123), resources accordion, link to Django admin for staff
3. **Project directory** — cards from API; click opens modal with metadata, related datasets, publications

Anchor link `#conducting-research-heading` scrolls below the fixed nav (via `scroll-padding-top`).

### `/data` features

- Search, filter by project / org / cadence / status
- Sortable columns
- Expand row: description, metadata schema, public files with download links
- “Manage dataset entry” → Django admin

### Homepage research highlights

Configured in [`src/lib/data/researchHighlights.ts`](../src/lib/data/researchHighlights.ts) — currently CFI, Knotweed Management, Forest Soil Monitoring. Uses the same card component as `/research`.

---

## 9. Making research and data visible to the public

**Admin changes do not automatically appear on the public site.** You must set visibility flags.

| To appear on… | Set on… | Flag |
|---------------|---------|------|
| `/research` project cards | Project | **Shared publicly** |
| `/data` dataset rows | Dataset | **Expose on public API** + status **Active** or **Archived** |
| `/data` file downloads | Dataset file | **Expose on public API** |
| `/research` publications | Project publication | **Expose on public API** |

### Bulk publish sample data

After seeding:

```bash
python backend/manage.py publish_sample_data
# or research projects only (no /data datasets):
python backend/manage.py publish_sample_data --research-only
```

### Checklist before telling stakeholders “it’s live”

- [ ] Django API responds: `curl http://127.0.0.1:8000/api/public/projects/`
- [ ] Expected projects have `shared_publicly=true`
- [ ] Expected datasets have `expose_on_public_api=true` and status active/archived
- [ ] Vercel `PUBLIC_DJANGO_API_BASE_URL` points at production API
- [ ] CORS allows the Vercel origin (production only)

---

## 10. Seed data and sample files

**Full runbook:** [SEED_DATA.md](SEED_DATA.md)

### Quick reference

| Command | When to use |
|---------|-------------|
| `seed_sample_projects --owner <user>` | Load/update 10 research project records |
| `seed_sample_datasets --owner <user>` | Import files from `src/lib/data/tff-sample-data/` |
| `seed_round_2 --owner <user>` | All-in-one catch-up (cleanup + projects + datasets) |
| `publish_sample_data` | Turn on public flags for sample content |
| `seed_research_publications --publish` | Load curated publications list |
| `cleanup_seed_duplicates` | Fix duplicate project slugs (safe anytime) |
| `audit_sample_data` | Compare disk folders vs database |

### Sample data folders → projects

| Folder | Project slug |
|--------|----------------|
| `knotweed/` | `knotweed-management-study` |
| `CFI/` | `forest-inventory-transect-study` |
| `breeding bird census/` | `breeding-bird-census` |
| `acorn planting/` | `acorn-planting` |
| `million tree plot/` | `million-tree-plot` |
| `soil monitoring/` | `soil-monitoring` |

**Rule:** Run `cleanup_seed_duplicates` before re-seeding if duplicates might exist. Do not run `seed_sample_projects` repeatedly without `--update` — it used to create duplicate slugs (fixed in code, but old DBs may need cleanup).

---

## 11. Public API reference (what the site reads)

Base URL: `{PUBLIC_DJANGO_API_BASE_URL}`

| Endpoint | Auth | Used by |
|----------|------|---------|
| `GET /api/public/projects/` | None | `/research`, home |
| `GET /api/public/datasets/` | None | `/data`, `/research` (related datasets) |
| `GET /api/public/datasets/?project=<slug>` | None | Filtered data views |
| `GET /api/public/publications/` | None | `/research` publications |
| `GET /api/public/datasets/<id>/files/<id>/download/` | None (desktop UA) | File downloads |

Authenticated researcher API (`/api/projects/`, `/api/datasets/`) is documented in [API_CONTRACT.md](../backend/API_CONTRACT.md). The custom `/projects` Svelte dashboard is **deprecated**; use Django admin instead.

---

## 12. Static site content (CSV files)

These live in `static/` and do **not** go through Django:

| File | Used for |
|------|----------|
| `static/announcements.csv` | Home hero background image (first row) |
| `static/events.csv` | Events (if enabled on a page) |
| `static/press.csv` | Press links |

Format: CSV with header row. Edit in Excel or a text editor, commit, deploy.

---

## 13. Production deployment

**Status (mid-2026):** Local development is active. AWS Organizations + dedicated grant member account is **on hold** until a unique root email is available.

When ready:

- **[DEPLOYMENT.md](DEPLOYMENT.md)** — Vercel frontend, EC2 Docker backend, RDS Postgres, S3 uploads, TLS, CORS
- **[README.md](../README.md)** — quick start

**Production checklist highlights:**

1. API behind HTTPS (`https://api.yourdomain.org`)
2. `USE_HTTPS=true` in production Django settings
3. Vercel env: `PUBLIC_DJANGO_API_BASE_URL=https://api.yourdomain.org`
4. `CSRF_TRUSTED_ORIGINS` and `CORS_ALLOWED_ORIGINS` include Vercel URL
5. Run migrations + `createsuperuser` on production DB (separate from local SQLite)
6. `publish_sample_data` after seeding on EC2

---

## 14. Common tasks (cheat sheet)

### Add a new research project to the public site

1. Reserve a Figshare DOI for the project ([Figshare guide](https://info.figshare.com/user-guide/how-to-reserve-a-doi/))
2. Admin → Projects → Add
3. Fill title, summary, description, organization, ongoing, partners, **Figshare item URL**
4. Check **Shared publicly**
5. Save
6. Optionally add datasets and publications

### Add a dataset with a file

1. Admin → Datasets → Add (or edit existing)
2. Set project, cadence, status **Active**, data type
3. Check **Expose on public API**
4. In Files inline: upload file or paste external URL; check **Expose on public API**
5. Save → verify on `/data`

### Add a publication to `/research`

1. Admin → Project publications → Add
2. Set citation, year, optional DOI/URL
3. Link to project (or leave blank for site-wide)
4. Check **Expose on public API**; optionally **Featured**
5. Save

### Onboard a new NYBG staff editor

1. `createsuperuser` (or create user in admin)
2. Set `UserProfile.role` to `internal_admin` (see [§6](#6-user-accounts-and-permissions))
3. Share `/admin/` URL and credentials via secure channel

### Refresh sample data after git pull

```bash
python backend/manage.py cleanup_seed_duplicates
python backend/manage.py seed_round_2 --owner <username> --publish
```

### Run tests (backend)

```bash
source .venv-local/bin/activate
python backend/manage.py test apps.datasets.tests.PublicApiTests
```

---

## 15. Troubleshooting

### “fetch failed” or empty `/research` / `/data`

- Is Django running? `python backend/manage.py runserver 127.0.0.1:8000`
- Is root `.env` `PUBLIC_DJANGO_API_BASE_URL` correct?
- Do records have `shared_publicly` / `expose_on_public_api`?

### Cannot log into Django admin

- Use **username**, not email
- Reset password: `python backend/manage.py changepassword <username>`
- User needs `is_staff=True` (from `createsuperuser`)
- Local vs production use **different databases** — create users on each environment

### `SyntaxError` when running `activate`

Use `source .venv-local/bin/activate`, not `python3 .venv-local/bin/activate`.

### API 403 “Authentication credentials were not provided”

- Expected for anonymous API calls to protected endpoints
- Public pages should only call `/api/public/*`
- Researcher management is via Django admin (same origin as API), not the SvelteKit site

### Duplicate projects in admin

```bash
python backend/manage.py cleanup_seed_duplicates
```

See [SEED_DATA.md § Why duplicates happened](SEED_DATA.md#why-duplicates-happened-ec2-june-2026).

### Dropdown menu hidden behind hero

Fixed via nav `overflow: visible` when INFO FOR menu is open. If it regresses, check `Nav.svelte`.

### Anchor links hidden under fixed nav

Global `scroll-padding-top: var(--site-nav-height)` in `src/styles/all.css`.

---

## 16. Related documentation

| Document | Contents |
|----------|----------|
| [README.md](../README.md) | Quick local start |
| [backend/README.md](../backend/README.md) | Backend setup, Docker |
| [SEED_DATA.md](SEED_DATA.md) | Seed commands, slugs, duplicate cleanup |
| [DEPLOYMENT.md](DEPLOYMENT.md) | AWS, Vercel, EC2, RDS, HTTPS |
| [backend/API_CONTRACT.md](../backend/API_CONTRACT.md) | Full REST API + roles |
| [backend/OVERDUE_DATA_ALERT_SPEC.md](../backend/OVERDUE_DATA_ALERT_SPEC.md) | Project alert spec (future) |

### Key code locations

| Area | Path |
|------|------|
| Public project serializer | `backend/apps/datasets/public_serializers.py` |
| Admin registration | `backend/apps/datasets/admin.py` |
| Role scoping | `backend/apps/accounts/roles.py` |
| Research page | `src/routes/research/+page.svelte` |
| Data page | `src/routes/data/+page.svelte` |
| Research card component | `src/lib/components/ResearchProjectCard.svelte` |
| Seed constants | `backend/apps/datasets/seed_constants.py` |
| Sample file config | `backend/apps/datasets/sample_data_config.py` |

### Handoff contact

Original development: Annie Fu (afu@nybg.org) — January 2026 onward.

For grant/AWS account setup questions, see [DEPLOYMENT.md § AWS account strategy](DEPLOYMENT.md#aws-account-strategy-grant-funded).

---

*When in doubt: manage content in Django admin, publish with the visibility flags, and verify on `/research` and `/data` with Django running.*
