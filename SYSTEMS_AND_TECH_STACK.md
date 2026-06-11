# Microforests DB — Systems Breakdown & Tech Stack Spec

**Purpose:** Document the NYBG `microforests-db` architecture so another project can replicate the same **database + backend + AWS deployment** pattern, with additions for a **public-facing frontend**.

**Reference repo:** `microforests-db` (Django monolith, admin-only HTTP surface today)

---

## Table of contents

1. [Executive summary](#1-executive-summary)
2. [Architecture (production)](#2-architecture-production)
3. [Architecture (local development)](#3-architecture-local-development)
4. [Tech stack (pinned versions)](#4-tech-stack-pinned-versions)
5. [Repository layout](#5-repository-layout)
6. [Data model (domain summary)](#6-data-model-domain-summary)
7. [Application behavior](#7-application-behavior)
8. [Docker Compose (production)](#8-docker-compose-production)
9. [Nginx configuration](#9-nginx-configuration)
10. [AWS infrastructure checklist](#10-aws-infrastructure-checklist)
11. [Environment variables (production)](#11-environment-variables-production)
12. [Extension blueprint: same backend + public frontend](#12-extension-blueprint-same-backend--public-frontend)
13. [Operations runbook (condensed)](#13-operations-runbook-condensed)
14. [Replication prompt for AI](#14-replication-prompt-for-ai)

---

## 1. Executive summary

| Layer | Technology |
|--------|------------|
| Language | Python 3.12 |
| Web framework | Django 5.0.6 + GeoDjango (PostGIS) |
| App server | Gunicorn (3 workers) |
| Reverse proxy / TLS | Nginx 1.27 (Docker) + Let's Encrypt (Certbot) |
| Compute | Single AWS EC2 (Ubuntu), Docker Compose |
| Database | **External** managed PostgreSQL + PostGIS (e.g. RDS); not in production Compose |
| Object storage | AWS S3 via `django-storages` + `boto3` (media/uploads) |
| Static assets | `collectstatic` → Docker volume → Nginx `/static/` |
| Primary UI | **Django Admin only** (`/admin/`) — no public site in this repo |
| Local dev | Docker Compose: `web` + `postgis/postgis:16-3.4` |

---

## 2. Architecture (production)

```mermaid
flowchart TB
  User[Browser / Admin users]
  DNS[DNS A record → Elastic IP]
  EC2[EC2 Ubuntu + Docker Compose]
  Nginx[Nginx container :80 :443]
  Web[Gunicorn / Django :8000 internal]
  RDS[(RDS PostGIS)]
  S3[(S3 bucket media)]
  Certbot[Certbot container on demand]

  User --> DNS --> Nginx
  Nginx -->|/static/ volume| Static[staticfiles volume]
  Nginx -->|proxy /| Web
  Web --> RDS
  Web --> S3
  Certbot -.->|HTTP-01| Nginx
  Certbot -.->|certs volume| Nginx
```

### Traffic path

1. Client → `https://<domain>` → EC2 security group (443 open).
2. Nginx terminates TLS, serves `/static/` from shared volume.
3. All other paths → `http://web:8000` (Gunicorn/Django).
4. Django uses `DATABASE_URL` (PostGIS) and S3 for `FileField` storage when `USE_S3=True`.

### Not in production Compose

Postgres container (database is RDS/external).

---

## 3. Architecture (local development)

```mermaid
flowchart LR
  Dev[Developer]
  Web[web container Django]
  DB[(postgis/postgis:16-3.4)]
  Dev -->|localhost via compose| Web
  Web --> DB
```

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml up
```

- `docker-compose.local.yml` adds `db` service and sets `DATABASE_URL` for `web`.
- `certbot` profile disabled locally.
- `manage.py` defaults to `config.settings.local` unless `.env` overrides.

---

## 4. Tech stack (pinned versions)

```yaml
runtime:
  python: "3.12-slim"  # Dockerfile base image
  os_prod: Ubuntu 24.04 LTS on EC2
  os_packages: gdal-bin, libgdal-dev, libpq-dev, gcc  # GeoDjango build/runtime

python_packages:
  Django: "5.0.6"
  psycopg2-binary: "2.9.9"
  pyproj: ">=3.6,<4"
  django-environ: "0.11.2"
  django-storages[s3]: "1.14.3"
  boto3: "1.34.131"
  gunicorn: unpinned

containers:
  web: built from repo Dockerfile
  nginx: nginx:1.27-alpine
  certbot: certbot/certbot:v3.0.1
  db_local_only: postgis/postgis:16-3.4

spatial:
  srid_primary: 2263  # NYC local projection on TreePoint.location
  engine: django.contrib.gis.db.backends.postgis
```

---

## 5. Repository layout

```
microforests-db/
├── config/
│   ├── settings/
│   │   ├── base.py          # DB, apps, S3, static, templates
│   │   ├── local.py         # DEBUG, localhost hosts
│   │   └── production.py    # TLS headers, HSTS, upload limits
│   ├── urls.py              # admin/ only today
│   ├── wsgi.py
│   └── admin_branding.py    # site_header, site_title (not site-packages)
├── apps/trees/              # sole domain app
│   ├── models.py            # Species, Plate, TreePoint, PlateFile, etc.
│   ├── admin.py             # ModelAdmin + custom CSV bulk upload views
│   ├── management/commands/ # bulk_import_plate_folders, bulk_upload_plate_trees
│   ├── plate_*_import.py    # CSV/folder import logic
│   └── templates/admin/     # change_list buttons, import_csv pages
├── templates/admin/         # project-level admin overrides (base_site, logged_out)
├── static/admin/css/        # nybg_admin.css overrides
├── deploy/
│   ├── EC2_DOCKER_RUNBOOK.md
│   ├── nginx/               # http.conf, https.conf → default.conf on server
│   └── scripts/             # init-letsencrypt.sh, renew-letsencrypt.sh
├── docs/
│   └── SYSTEMS_AND_TECH_STACK.md  # this file
├── docker-compose.yml       # production stack: web, nginx, certbot
├── docker-compose.local.yml # overlay: db + local DATABASE_URL
├── Dockerfile
├── requirements.txt
├── env.production.example
└── .env.example             # local secrets template (not committed)
```

### Critical convention

**Never customize Django under `.venv/` or `.venv.windows/`.** Use `templates/`, `static/`, and `config/` for UI and branding. Docker installs Django from PyPI; venv edits are not deployed.

---

## 6. Data model (domain summary)

PostgreSQL + PostGIS. Core entities in `apps.trees`:

| Model | Role |
|--------|------|
| `Species` | Taxon codes + common names |
| `Plate` | Survey plate metadata (park, borough, date, zotero_id, notes) |
| `TreePoint` | GIS point per tree (`PointField` SRID 2263), links plate + species |
| `PlateFile` | Files per plate (georef TIFF, HTML report) → S3 when `USE_S3=True` |
| `PlateSpecies` | M2M legend: species on a plate |
| `MissingSpeciesCode` | Tracking unknown codes per plate |

### Import paths

| Method | Use case |
|--------|----------|
| Admin CSV — plates | Bulk plate metadata (`Plate`, `Park`, `Borough`, `Date`, …) |
| Admin CSV — species | Plate–species legend rows |
| Admin CSV — tree points | Per-plate tree CSV (coordinates, species codes, stems) |
| CLI `bulk_import_plate_folders` | One host folder per plate: CSV + `*_georef.tif` + optional HTML report |

CLI imports require mounting host data into the container:

```bash
docker compose run --rm \
  -v /home/ubuntu/plate-import:/data/plates:ro \
  web python manage.py bulk_import_plate_folders /data/plates --no-input
```

---

## 7. Application behavior

### 7.1 URL routing (current)

```python
urlpatterns = [
    path("admin/", admin.site.urls),
]
# DEBUG only: Django serves static locally
```

**Implication:** Production HTTP surface is **admin + static**. No REST/GraphQL, no public templates.

### 7.2 Admin extensions pattern

1. `change_list_template` → add “Bulk upload CSV” link in object tools.
2. Custom `get_urls()` → register `bulk-upload-csv/` view.
3. Form upload → parse UTF-8 CSV (comma or tab) → validate → optional dry-run.
4. Optional session “checkpoint” forms (e.g. create missing `Plate` mid-import).

### 7.3 Settings split

| Module | When | Key flags |
|--------|------|-----------|
| `config.settings.local` | Dev (`manage.py` default) | `DEBUG=True`, localhost `ALLOWED_HOSTS` |
| `config.settings.production` | EC2 `.env` | `SECURE_SSL_REDIRECT`, HSTS, `CSRF_TRUSTED_ORIGINS`, 300MB upload limits |

Environment loaded via `django-environ` from `/app/.env` in container.

### 7.4 Storage

```yaml
USE_S3: false  # local: MEDIA_ROOT on disk
USE_S3: true   # prod: FileField → S3Boto3Storage

staticfiles:
  collected to staticfiles volume
  Nginx serves /static/
  NOT on S3 in current config

credentials:
  prod_preferred: EC2 IAM instance role (no keys in .env)
  dev_optional: AWS_ACCESS_KEY_ID + SECRET in .env
```

---

## 8. Docker Compose (production)

```yaml
services:
  web:
    build: .
    expose: ["8000"]           # not published to host
    env_file: .env
    volumes:
      - static_data:/app/staticfiles
    command: collectstatic && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
    healthcheck: TCP :8000

  nginx:
    image: nginx:1.27-alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./deploy/nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
      - static_data:/app/staticfiles:ro
      - certbot_www, letsencrypt volumes
    depends_on: web healthy

  certbot:
    # cert issuance/renewal; shares volumes with nginx

volumes:
  static_data, certbot_www, letsencrypt
```

### Deploy application code

```bash
git pull
docker compose build web
docker compose up -d --force-recreate web
```

### Deploy nginx config only (bind mount; no image rebuild)

```bash
DOMAIN=your-domain.com
sed "s/__DOMAIN_NAME__/$DOMAIN/g" deploy/nginx/https.conf > deploy/nginx/default.conf
docker compose exec nginx nginx -t
docker compose exec nginx nginx -s reload
```

### Host data not baked into image

Large plate folders on EC2 (e.g. `/home/ubuntu/plate-import`) are mounted at runtime for management commands only.

---

## 9. Nginx configuration

| File | Use |
|------|-----|
| `deploy/nginx/http.conf` | Initial HTTP + ACME challenge + proxy |
| `deploy/nginx/https.conf` | Template with `__DOMAIN_NAME__` placeholders |
| `deploy/nginx/default.conf` | **Active on server** — overwritten by `init-letsencrypt.sh` |

### Production HTTPS essentials

```nginx
client_max_body_size 300M;
proxy_read_timeout 300s;
proxy_send_timeout 300s;

location /static/ {
    alias /app/staticfiles/;
}

location / {
    proxy_pass http://web:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto https;
}
```

### TLS

- Issued via `deploy/scripts/init-letsencrypt.sh`
- Renewed via cron + `deploy/scripts/renew-letsencrypt.sh`

### Common nginx issue

After `git pull`, `default.conf` on the server may still show old limits (e.g. `50M`). Regenerate from `https.conf` or `sed` in place, then `nginx -s reload`. Confirm:

```bash
docker compose exec nginx grep client_max_body_size /etc/nginx/conf.d/default.conf
```

---

## 10. AWS infrastructure checklist

```yaml
ec2:
  ami: Ubuntu 24.04 LTS
  instance_type: t3.small recommended (t3.micro risks OOM with Docker)
  elastic_ip: attached for stable DNS
  iam_role: S3 access for media bucket; optional SSM for Session Manager
  security_group_inbound:
    - 22: operator IPs only (avoid 0.0.0.0/0 in production)
    - 80: 0.0.0.0/0
    - 443: 0.0.0.0/0
  subnet: public subnet with route 0.0.0.0/0 → Internet Gateway

rds:
  engine: PostgreSQL + PostGIS extension
  connection: DATABASE_URL in .env (sslmode=require typical)
  security_group: allow EC2 → port 5432

s3:
  bucket: private; EC2 IAM role or keys
  use: user uploads (PlateFile), not collected Django static

dns:
  A_record: domain → Elastic IP

backup:
  rds_snapshots: scheduled
  s3_lifecycle: as needed for large TIFFs
```

### Common failure modes (observed)

| Symptom | Likely cause |
|---------|----------------|
| SSH/HTTPS timeout, instance status check failed | OOM on `t3.micro`; add swap or upgrade instance |
| `413 Request Entity Too Large` | `client_max_body_size` too low in active `default.conf` |
| UI changes not visible after deploy | Edits were in `.venv`; must use `templates/` + `static/` + rebuild `web` |
| `nc` / curl timeout despite open SG | Subnet missing IGW route, or instance unhealthy |
| SSM agent offline | Missing `AmazonSSMManagedInstanceCore` on instance IAM role |

---

## 11. Environment variables (production)

```bash
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<django-secret>
DEBUG=False
ALLOWED_HOSTS=example.org,www.example.org
CSRF_TRUSTED_ORIGINS=https://example.org,https://www.example.org
SECURE_HSTS_SECONDS=31536000

DATABASE_URL=postgis://USER:PASS@host:5432/dbname?sslmode=require

USE_S3=True
AWS_STORAGE_BUCKET_NAME=my-bucket
AWS_S3_REGION_NAME=us-east-1
# omit AWS_ACCESS_KEY_ID / SECRET if using IAM role on EC2

DOMAIN_NAME=example.org
LETSENCRYPT_EMAIL=admin@example.org
```

See `env.production.example` in repo root.

---

## 12. Extension blueprint: same backend + public frontend

This repo is **admin-backend-only**. For a sibling project with a public site, keep the same infra; extend the application layer.

### 12.1 Target architecture

```mermaid
flowchart TB
  subgraph clients [Clients]
    Public[Public users]
    Staff[Staff / editors]
  end

  Nginx[Nginx]
  Django[Django Gunicorn]
  FE[Option A: Django templates + views]
  API[Option B: Django REST / Ninja API]
  SPA[Option C: Separate SPA on S3+CloudFront or Vercel]

  RDS[(PostGIS)]
  S3[(S3)]

  Public --> Nginx
  Staff --> Nginx
  Nginx -->|/static/| Static
  Nginx -->|/admin/| Django
  Nginx -->|/api/ or /| Django
  Nginx -.->|optional /assets| SPA
  Django --> RDS
  Django --> S3
  FE --> Django
  API --> Django
  SPA --> API
```

### 12.2 Nginx routing (add to `https.conf`)

```nginx
location /static/ { alias /app/staticfiles/; }

# Optional: only if Django serves media locally instead of direct S3 URLs
location /media/ { proxy_pass http://web:8000; }

location /admin/ {
    proxy_pass http://web:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto https;
}

location /api/ {
    proxy_pass http://web:8000;
    # same proxy headers
}

location / {
    # Option A: Django public pages
    proxy_pass http://web:8000;

    # Option C: separate frontend container
    # proxy_pass http://frontend:3000;
}
```

### 12.3 Django changes for public project

```yaml
new_apps:
  - apps.public     # views, templates, URLs
  - apps.api        # optional DRF or django-ninja

urls:
  - path("", include("apps.public.urls"))
  - path("api/", include("apps.api.urls"))
  - path("admin/", admin.site.urls)

settings_additions:
  CORS_ALLOWED_ORIGINS: if SPA on another origin
  REST_FRAMEWORK: pagination, permissions

auth:
  admin: Django staff / superusers
  public_read: AllowAny or anonymous for catalog views
  public_write: usually none; staff via admin or API tokens

caching_optional:
  CloudFront in front of S3 for media
  Redis for session/cache if traffic grows
```

### 12.4 What to copy verbatim

| Component | Reuse? |
|-----------|--------|
| Dockerfile + GDAL deps | Yes, if GeoDjango needed |
| `docker-compose.yml` nginx/certbot pattern | Yes |
| `deploy/scripts/init-letsencrypt.sh` | Yes |
| `config/settings` base/production + django-environ | Yes |
| S3 storage block in `base.py` | Yes |
| RDS PostGIS + `DATABASE_URL` | Yes |
| Admin CSV import pattern | Yes, per model |
| `deploy/EC2_DOCKER_RUNBOOK.md` | Yes; adjust instance size |

### 12.5 What to add for public frontend

| Need | Suggestion |
|------|------------|
| Public pages | Django views + templates **or** Next.js/React SPA |
| API | `djangorestframework` or `django-ninja` |
| SEO | Server-rendered templates or SSR framework |
| Media URLs | S3 presigned URLs or public-read prefix + CloudFront |
| API auth | Session (same domain) or JWT for SPA |
| Rate limiting | Nginx `limit_req` or Django middleware |
| Separate deploy | Optional: frontend on Amplify/Vercel; API on same EC2 |

---

## 13. Operations runbook (condensed)

Full step-by-step: `deploy/EC2_DOCKER_RUNBOOK.md`

```yaml
provision:
  - EC2 + Elastic IP + security group + IAM role (S3)
  - RDS PostGIS; security group allows EC2 on 5432
  - S3 bucket
  - git clone; cp env.production.example → .env; fill secrets
  - docker compose build && docker compose up -d web nginx
  - docker compose exec web python manage.py migrate
  - ./deploy/scripts/init-letsencrypt.sh <domain> <email>
  - crontab: renew-letsencrypt.sh daily

deploy_app:
  - git pull
  - docker compose build web
  - docker compose up -d --force-recreate web
  - migrate if models changed

deploy_nginx_only:
  - update deploy/nginx/default.conf (or regenerate from https.conf)
  - docker compose exec nginx nginx -t && nginx -s reload

bulk_data:
  - plate metadata: Admin → Plates → Bulk upload plates CSV
  - species legend: Admin → Species → Bulk upload species CSV
  - tree points: Admin → Tree points → Bulk upload CSV
  - folder batch: bulk_import_plate_folders + volume mount

monitoring:
  - EC2 status checks: 2/2 passed
  - docker compose ps
  - df -h and free -m on small instances
```

---

## 14. Replication prompt for AI

Copy-paste to bootstrap a similar project:

> Build a Django 5 + GeoDjango + PostGIS project deployed like `microforests-db`: single EC2 with Docker Compose (`web` Gunicorn, `nginx` TLS, `certbot`), external RDS PostGIS, S3 via django-storages, `django-environ` settings split (`local` / `production`), Nginx serving `/static/` from a volume and proxying to Gunicorn with `client_max_body_size 300M`, Let's Encrypt via `init-letsencrypt.sh`. Include Django Admin with custom CSV bulk-import views. **Additionally**, add a public-facing frontend at `/` (Django templates or React SPA + REST API at `/api/`), with `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and Nginx locations for `/`, `/admin/`, and `/api/`. Do not patch packages in `.venv`; use `templates/` and `static/` for UI. Local dev uses `docker-compose.local.yml` with `postgis/postgis:16-3.4`. See `docs/SYSTEMS_AND_TECH_STACK.md` for full architecture.

---

## Related docs in this repo

| File | Contents |
|------|----------|
| `deploy/EC2_DOCKER_RUNBOOK.md` | Step-by-step EC2 provisioning and deploy |
| `env.production.example` | Production environment template |
| `.env.example` | Local development environment template |
| `LOCAL_TEST_DEBUG_RUNBOOK.md` | Local Docker debugging |

---

*Last aligned with repo stack: Django 5.0.6, Python 3.12, Nginx 300M upload limit, admin-only public HTTP surface.*
