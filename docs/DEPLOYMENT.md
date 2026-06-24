# Deployment: Vercel + EC2 (Docker) + RDS + S3

Runbook for the **TFF Thain Family Forest website + database backend**: public site on Vercel, Django API on EC2 (Docker), PostgreSQL on RDS, and (recommended) object storage on S3 in a **grant-isolated AWS member account**.

## Status (read this first)

| Track | Status |
|-------|--------|
| **Local development** | **Active now** — see [README](../README.md#active-development-now) |
| **AWS Organizations + member account** | **Deferred** — resume when you have a unique root email for the TFF account ([troubleshooting](#troubleshooting-email-already-in-use-when-creating-a-member-account)) |
| **Vercel + EC2 + RDS + S3** | Planned; follow sections below after AWS account exists |

Nothing in this doc blocks day-to-day feature work. You can build against SQLite or local Docker Postgres on your laptop without touching AWS.

### When you resume AWS setup

1. Obtain a unique root email (plus-alias or work alias).
2. Create the member account (or invite an existing account) — [Step-by-step](#step-by-step-member-account-setup).
3. Provision RDS + EC2 in that account — [§1 RDS](#1-amazon-rds), [§2 EC2](#2-ec2--docker).
4. Deploy the frontend to Vercel with `PUBLIC_DJANGO_API_BASE_URL` — [§3 Vercel](#3-vercel-frontend).

---

## Architecture

When deployed, grant-funded AWS resources should live in a **dedicated member account** (see [AWS account strategy](#aws-account-strategy-grant-funded)). Legacy workloads stay in your existing root (management) account.

```mermaid
flowchart TB
  subgraph vercel [Vercel]
    fe[SvelteKit_frontend]
  end
  subgraph member [TFF_member_account]
    ec2[EC2_Docker_Gunicorn]
    rds[(RDS_PostgreSQL)]
    s3[(S3_uploads)]
  end
  subgraph mgmt [Management_account_existing_root]
    legacy[Legacy_EC2_and_other_resources]
  end
  fe -->|HTTPS_PUBLIC_DJANGO_API| ec2
  ec2 --> rds
  ec2 --> s3
```

| Component | Host | Role |
|-----------|------|------|
| **Vercel** | Vercel | SvelteKit site, static assets, SSR for `/research` and `/data` |
| **EC2 + Docker** | TFF member account | Django API, admin, upload handling ([`backend/Dockerfile`](../backend/Dockerfile)) |
| **RDS** | TFF member account | Metadata, users, permissions, dataset records |
| **S3** | TFF member account | Dataset files, publications, large binaries (Phase 2) |

- **Vercel** does not run Django and does not connect to RDS directly.
- **RDS** is reachable only from the EC2 security group (same VPC in the member account).
- **S3** holds uploaded blobs; RDS stores pointers and metadata (see [Data shapes and storage](#data-shapes-and-storage)).

---

## AWS account strategy (grant-funded)

### FAQ: Root already has many instances — should I create an Organization?

**Short answer:** Enabling AWS Organizations on your current root account **does not migrate or reconfigure** existing EC2 instances. They stay in the same account, which becomes the **management account**. Operations on those instances are largely unchanged.

| Aspect | Effect |
|--------|--------|
| Existing EC2 / RDS / S3 in root | Unchanged ARNs and console locations |
| Account role | Root becomes **management account** (permanent; cannot be reassigned later) |
| Billing | Consolidated bill across linked accounts; grant spend visible per **member account** |
| New TFF work | **Deploy EC2, RDS, and S3 in a new member account**, not in root |
| Service Control Policies (SCPs) | Optional org guardrails — design carefully so root workloads are not blocked |
| Complexity | More IAM/org concepts; **not** a forced rebuild of current infrastructure |

AWS’s UI recommends an empty account as the management account. In practice, many teams enable Organizations on an account that already has resources. The important part for grant separation is: **put all TFF infrastructure in a member account**, and keep personal/other projects in root (or other member accounts).

### Recommended layout (default)

1. **Enable AWS Organizations** on your existing root account (it becomes the management account).
2. **Create a member account** (e.g. `tff-nybg-prod`) for all grant-funded resources.
3. **Do not move** legacy EC2 into the member account unless you deliberately migrate later.
4. **Tag and budget** the member account for grant reporting.

```mermaid
flowchart TB
  subgraph org [AWS_Organization]
    mgmt[ManagementAccount_existing_root]
    tff[TFF_member_account_new]
  end
  mgmt -->|"existing EC2 unchanged"| legacy[Legacy_resources]
  tff --> ec2[EC2_Docker]
  tff --> rds[RDS]
  tff --> s3[S3_uploads]
```

### Alternatives

| Approach | Grant billing separation | Notes |
|----------|------------------------|--------|
| **Org + member account** (recommended) | Strong — filter Cost Explorer by linked account | Consolidated bill; one payer, clear TFF line item |
| **Standalone new AWS account** (no Org) | Strong — separate bill entirely | No consolidated CUR across accounts; simpler if TFF is the only AWS use for grants |
| **Cost tags only in root** | Weak — shared account noise | Easiest; harder to prove TFF-only spend for auditors |

### Step-by-step: member account setup

1. **AWS Organizations** → Create organization (management account = current root).
2. **Add account** → Create new account (email alias, e.g. `tff-aws@yourdomain.org`) → note account ID.
3. **Access:** Use IAM Identity Center (SSO) or a cross-account admin role from management → member account.
4. **In the member account only:**
   - VPC (or default VPC for early staging), subnets, security groups
   - RDS PostgreSQL (private subnets)
   - EC2 for Docker
   - S3 bucket for uploads (block public access; access via IAM role on EC2)
5. **Do not** provision TFF EC2/RDS in root unless you accept mixed billing.

### Troubleshooting: “Email already in use” when creating a member account

AWS requires a **unique root email per account**. The address cannot be the same as your management (root) account, any other member account, or any standalone AWS account you created in the past—even if that account is closed or barely used.

**Fixes (pick one):**

| Approach | What to do |
|----------|------------|
| **Plus-alias (Gmail, Outlook, many providers)** | Use a new root email that still reaches you, e.g. `you+tff-nybg@gmail.com` or `you.aws.tff@outlook.com`. AWS treats it as a separate account; mail often still delivers to `you@gmail.com`. |
| **Different mailbox** | Use a work address (`afu@nybg.org`) if root uses personal, or a dedicated alias from IT (`tff-aws@nybg.org`). |
| **Invite an existing account** | If you already opened a second AWS account with another email, use Organizations → **Add account** → **Invite existing AWS account** instead of **Create account**. |
| **Standalone account (no Org)** | Sign up at [aws.amazon.com](https://aws.amazon.com) with a fresh email, use that account only for TFF, and skip Organizations until later. Grant billing is still isolated on that account’s bill. |

**Avoid:**

- Reusing the **same** email as your current root/login account.
- Reusing an email that was the root of an old AWS account you forgot about (check inbox for past “Welcome to Amazon Web Services” messages).

**After a successful create:** AWS sends a verification email to the **new** root address; complete that before the account is fully active. Sign in to the member account via Organizations → select account → **Access this account** (or IAM Identity Center), not the root email of the management account.

### Billing controls (grant reporting)

Apply in the **TFF member account**:

| Control | Purpose |
|---------|---------|
| **Cost allocation tags** | `Project=TFF`, `GrantId=<grant-number>`, `Environment=prod` on EC2, RDS, S3, data transfer |
| **Tag policies** (Organizations) | Require `Project` tag on creatable resources in member account |
| **AWS Budgets** | Monthly budget on member account ID with email alert at 80% / 100% |
| **Cost Explorer** | Filter by linked account = TFF member account; group by service and tag |
| **CUR (optional)** | Cost and Usage Report to S3 in management or member account for formal grant closeouts |

**What stays in root:** Document explicitly (e.g. personal sites, other NYBG non-TFF infra) so TFF resources are never created there by mistake.

**Caution:** Avoid broad restrictive SCPs at the org level until you confirm they do not affect existing root workloads.

---

## Data shapes and storage

Sample uploads live under [`src/lib/data/tff-sample-data/`](../src/lib/data/tff-sample-data/) (six example projects). Use them as a **reference for formats and scale**, not as production data to deploy to Vercel.

### Sample inventory (18 files)

| Project folder | Example files | Sizes (approx.) | Suggested `data_type` | Suggested `file_kind` |
|----------------|---------------|-----------------|----------------------|------------------------|
| **CFI** | Field Work Manual PDF; Understory / Overstory `.xlsx` | 14 MB PDF; ~1.2–1.5 MB sheets | `document_archive` + `tabular` | `documentation` + `primary_data` |
| **breeding bird census** | `.pptx`, `.xlsx`, NYS BBA handbook PDF | 7 MB deck; ~295 KB data | `biodiversity_observation` or `tabular` | `documentation` + `primary_data` |
| **acorn planting** | Ten-tallest method PDF; plot `.xlsx` | 3.4 MB PDF; 18 KB data | `document_archive` + `tabular` | `documentation` + `primary_data` |
| **knotweed** | Haight et al. PDF; `NYBG_FALLOPIA` `.xls` | 554 KB; 100 KB | `document_archive` + `tabular` | `documentation` + `primary_data` |
| **million tree plot** | Survival paper PDFs; `101-1` `.xlsx` | up to ~543 KB | `tabular` + `document_archive` | mixed `documentation` + `primary_data` |
| **soil monitoring** | Sampling PDFs; FEMC `.xlsx` | up to ~1.5 MB | `tabular` + `document_archive` | `documentation` + `primary_data` |

Import into Django with `seed_sample_datasets` (run after `seed_sample_projects` for knotweed and CFI):

```bash
python backend/manage.py seed_sample_datasets --owner <username>
docker compose -f docker-compose.prod.yml exec backend python backend/manage.py seed_sample_datasets --owner <username>
```

| Sample folder | `Project.slug` | Links to existing research project? |
|---------------|----------------|-------------------------------------|
| knotweed | `knotweed-management-study` | Yes |
| CFI | `forest-inventory-transect-study` | Yes |
| breeding bird census | `breeding-bird-census` | Creates data-only project |
| acorn planting | `acorn-planting` | Creates data-only project |
| million tree plot | `million-tree-plot` | Creates data-only project |
| soil monitoring | `soil-monitoring` | Creates data-only project |

### File formats and upload policy

Observed formats: **`.xlsx`, `.xls`, `.pdf`, `.pptx`**.

Current API policy ([`backend/API_CONTRACT.md`](../backend/API_CONTRACT.md)):

- **≤ 100 MB:** direct upload allowed (all samples qualify; largest ~14 MB).
- **100 MB – 1 GB:** upload allowed; external link preferred.
- **> 1 GB:** external URL required.

Each real project typically has **multiple files** (raw tables, manuals, proposals, presentations). Model as one `Project` → one or more `Dataset` rows → multiple `DatasetFile` rows with `file_kind` (`primary_data`, `documentation`, `derived_output`, etc.).

### Slug mapping (`seed_sample_datasets`)

| Sample folder | `Project.slug` | Notes |
|---------------|----------------|-------|
| knotweed | `knotweed-management-study` | Links to research project from `seed_sample_projects` |
| CFI | `forest-inventory-transect-study` | Links to research project from `seed_sample_projects` |
| breeding bird census | `breeding-bird-census` | Creates data-only project if missing |
| acorn planting | `acorn-planting` | Creates data-only project if missing |
| million tree plot | `million-tree-plot` | Creates data-only project if missing |
| soil monitoring | `soil-monitoring` | Creates data-only project if missing |

### Storage architecture

```mermaid
flowchart LR
  user[Researcher_upload] --> api[Django_on_EC2]
  api --> rds[(RDS_metadata)]
  api --> s3[(S3_objects)]
  public[Vercel_public_pages] --> api
  api -->|presigned_or_public_URL| s3
```

| Layer | Stores |
|-------|--------|
| **RDS** | Users, organizations, projects, datasets, metadata schema/values, file version records, alert state |
| **S3** | PDF, Excel, PPTX, and other blobs (recommended production target) |
| **EC2 volume** | Staging only in early deploys |

**Recommended S3 key layout:**

```text
s3://<bucket>/datasets/{project_slug}/{dataset_id}/v{version}/{filename}
```

Optional later: CloudFront for public downloads, `publications/` prefix for `DatasetPublication` attachments.

### Storage phases

| Phase | Implementation | When |
|-------|----------------|------|
| **1 (current)** | Docker volume `media_data` in [`docker-compose.prod.yml`](../docker-compose.prod.yml) | Staging / low traffic |
| **2 (recommended)** | S3 + `django-storages`, IAM role on EC2, env vars in [`backend/.env.production.example`](../backend/.env.production.example) | Before heavy researcher uploads |
| **3 (optional)** | Antivirus scan, per-org quotas, geospatial rasters, Excel preview derivatives | As requirements grow |

### Repo note on sample binaries

`src/lib/data/tff-sample-data/` is for **planning and import scripts**, not for the Vercel frontend bundle. If the repo grows large, consider Git LFS or keeping samples outside git and documenting an S3 staging prefix instead.

---

## 1. Amazon RDS

Provision RDS in the **TFF member account**, same VPC as EC2 (default for a single-account deploy).

1. Create PostgreSQL (e.g. 16.x) in **private subnets**.
2. Security group **inbound:** PostgreSQL (5432) from the EC2 instance security group only.
3. Enable encryption and automated backups for production.
4. Set `DATABASE_URL` or `POSTGRES_*` in `backend/.env` on EC2 (see [`backend/.env.production.example`](../backend/.env.production.example)).

```text
postgresql://USER:PASSWORD@ENDPOINT.region.rds.amazonaws.com:5432/DATABASE
```

Use `POSTGRES_SSLMODE=require` for RDS.

---

## 2. EC2 + Docker

### Instance

- Amazon Linux 2023 or Ubuntu 22.04; Docker and Docker Compose installed.
- **Member account only** for grant isolation.
- Security group: SSH (22) from your IP; 80/443 from internet if using nginx/ALB; avoid exposing 8000 publicly without TLS.

### Deploy steps

```bash
git clone <repo-url> tff-website && cd tff-website
cp backend/.env.production.example backend/.env
# Edit: RDS, DJANGO_SECRET_KEY, domains, CORS, optional S3 vars
docker compose -f docker-compose.prod.yml up --build -d
docker compose -f docker-compose.prod.yml ps   # service name is backend, not web
docker compose -f docker-compose.prod.yml exec backend python backend/manage.py seed_sample_projects --owner <username> --update
docker compose -f docker-compose.prod.yml exec backend python backend/manage.py seed_sample_datasets --owner <username>
```

Entrypoint: migrations → `collectstatic` → Gunicorn ([`backend/docker-entrypoint.sh`](../backend/docker-entrypoint.sh)).

If `exec` fails with **service "web" is not running** (or **service "backend" is not running**), start the stack with `up -d` first, or check `docker compose -f docker-compose.prod.yml ps` and `logs backend`. The production compose file defines one service: **`backend`** ([`docker-compose.prod.yml`](../docker-compose.prod.yml)).

### TLS (recommended)

- **ALB** → target group EC2:8000, health check `GET /api/public/projects/`
- **ACM** certificate for `api.yourdomain.org`
- Update `DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`

### Uploaded files

See [Storage phases](#storage-phases). Phase 1 uses `backend/media/` on volume `media_data`. **Before production uploads at scale, complete Phase 2 (S3).**

---

## 3. Vercel (frontend)

1. Import the GitHub repo (root = project root).
2. Framework: **SvelteKit** ([`vercel.json`](../vercel.json)).
3. Production environment variable:

| Variable | Example |
|----------|---------|
| `PUBLIC_DJANGO_API_BASE_URL` | `https://api.yourdomain.org` |

Point at the API hostname in the **TFF member account** (ALB or nginx), not `localhost`. Redeploy after env changes.

Use `@sveltejs/adapter-vercel` if `adapter-auto` does not detect Vercel in CI.

### CORS / sessions

- **Public pages** (`/research`, `/data`): unauthenticated public API; no cookies.
- **Researcher dashboard** (`/projects`): session cookies across Vercel → EC2 require matching `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS`, HTTPS, and possibly `SESSION_COOKIE_SAMESITE=None` in prod settings.

Early staging: use EC2-hosted Django admin only; keep Vercel read-only until cross-origin login is verified.

### Before making the API public (HTTPS checklist)

Staging today uses **`http://EC2_IP:8000`** with **`USE_HTTPS=false`** in `backend/.env` so admin CSRF cookies work over HTTP. **Do not ship that configuration to real users.**

Before opening the API to the internet or the focus group:

1. Put the API behind **TLS** (`https://api.yourdomain.org` via ALB or nginx + ACM).
2. Set **`USE_HTTPS=true`** on EC2 and restart Docker (`config/settings/prod.py` ties secure cookies to this flag).
3. Update **`CSRF_TRUSTED_ORIGINS`**, **`CORS_ALLOWED_ORIGINS`**, **`DJANGO_ALLOWED_HOSTS`**, and Vercel **`PUBLIC_DJANGO_API_BASE_URL`** to `https://` URLs (drop raw EC2 IP origins).
4. Restrict EC2 security group: **no public port 8000**; only load balancer → EC2.
5. Plan **`SESSION_COOKIE_SAMESITE=None`** if `/projects` login from Vercel still fails after HTTPS.

Cursor rule `.cursor/rules/public-api-https.mdc` reminds the agent to surface this list when you ask about going public.

---

## 4. Smoke tests

```bash
curl https://api.yourdomain.org/api/public/projects/
curl "https://api.yourdomain.org/api/public/datasets/?project=knotweed-management-study"

# On EC2 (service name is backend — not web)
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml exec backend python backend/manage.py createsuperuser
docker compose -f docker-compose.prod.yml exec backend python backend/manage.py seed_sample_projects --owner <username> --update
docker compose -f docker-compose.prod.yml exec backend python backend/manage.py seed_sample_datasets --owner <username>
```

---

## 5. Local vs production compose

| File | Use |
|------|-----|
| [`docker-compose.yml`](../docker-compose.yml) | Local dev: Postgres container + Django runserver |
| [`docker-compose.prod.yml`](../docker-compose.prod.yml) | EC2: Django + Gunicorn → RDS |

### Local backend (venv, no Docker)

From the repo root on macOS / Linux:

```bash
python3.12 -m venv .venv-local          # first time only
source .venv-local/bin/activate         # every new terminal session
pip install -r backend/requirements.txt # first time or after dependency changes

cp backend/.env.example backend/.env    # set USE_SQLITE=true for SQLite
python backend/manage.py migrate
python backend/manage.py createsuperuser
python backend/manage.py seed_sample_projects --owner <your-username>
python backend/manage.py seed_sample_datasets --owner <your-username>
python backend/manage.py runserver 127.0.0.1:8000
```

Windows PowerShell: use `.venv-local\Scripts\Activate.ps1` instead of `source .venv-local/bin/activate`.

Use `python backend/manage.py seed_sample_projects --owner <user> --update` to refresh metadata on projects that already exist (matched by slug).

Local frontend (root [`.env.example`](../.env.example)):

```bash
PUBLIC_DJANGO_API_BASE_URL=http://127.0.0.1:8000
```

---

## Related docs

- [`backend/README.md`](../backend/README.md) — API setup, migrations
- [`backend/API_CONTRACT.md`](../backend/API_CONTRACT.md) — upload governance, endpoints
- [`backend/OVERDUE_DATA_ALERT_SPEC.md`](../backend/OVERDUE_DATA_ALERT_SPEC.md) — alert automation (future)

### Optional follow-up (not in this doc)

- Implement S3 + presigned uploads in Django
- `.gitignore` / Git LFS policy for sample binaries
