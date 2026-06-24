# Seed data runbook

How to load research project metadata and `tff-sample-data` files without creating duplicate admin rows.

**Commands:**

| Command | Purpose |
|---------|---------|
| `seed_sample_projects` | 6 research projects (metadata only) |
| `seed_sample_datasets` | 18 sample files → datasets on existing projects |
| `seed_round_2` | **All-in-one**: cleanup + research metadata + sample files + data-only projects |
| `cleanup_seed_duplicates` | Merge wrong-slug duplicates onto canonical slugs |

Canonical slugs and alias mappings live in [`backend/apps/datasets/seed_constants.py`](../backend/apps/datasets/seed_constants.py).

---

## Before you change or re-run seeds

1. **Pull latest code** and rebuild Docker on EC2 (`docker compose -f docker-compose.prod.yml up --build -d`).
2. **Run cleanup first** if duplicates might exist (safe to run anytime):

   ```bash
   # Local
   source .venv-local/bin/activate
   python backend/manage.py cleanup_seed_duplicates

   # EC2
   docker compose -f docker-compose.prod.yml exec backend python backend/manage.py cleanup_seed_duplicates
   ```

   Preview without changes: add `--dry-run`.

3. **Do not** run `seed_sample_projects` repeatedly hoping to “fix” the list — that created duplicates on EC2 before the slug fix (see below).

---

## Safe workflows

### First-time setup (local)

```bash
source .venv-local/bin/activate
pip install -r backend/requirements.txt

python backend/manage.py migrate
python backend/manage.py createsuperuser

python backend/manage.py seed_sample_projects --owner <username>
python backend/manage.py seed_sample_datasets --owner <username>
```

For data-only projects (breeding bird, acorn planting, etc.) that are not in `seed_sample_projects`, either run cleanup after creating them once, or:

```bash
python backend/manage.py seed_sample_datasets --owner <username> --create-missing-projects
```

### Refresh research metadata only

Use when you edit [`seed_sample_projects.py`](../backend/apps/datasets/management/commands/seed_sample_projects.py) (summaries, CFI short title, etc.):

```bash
python backend/manage.py cleanup_seed_duplicates
python backend/manage.py seed_sample_projects --owner <username> --update
```

`--update` applies new fields to the canonical project row. The command **consolidates alias slugs first** and will not create a second `filling-in-the-gaps` if `filling-in-the-gaps-plant-establishment-after-hurricane-sandy` still exists.

### Link or refresh sample files only

Use when you edit [`seed_sample_datasets.py`](../backend/apps/datasets/management/commands/seed_sample_datasets.py) or add files under `src/lib/data/tff-sample-data/`:

```bash
python backend/manage.py seed_sample_datasets --owner <username>
# Replace existing file blobs:
python backend/manage.py seed_sample_datasets --owner <username> --update
# One folder only:
python backend/manage.py seed_sample_datasets --owner <username> --folder knotweed
```

Does **not** create projects by default. Knotweed and CFI files attach to `knotweed-management-study` and `forest-inventory-transect-study`.

### Seed round 2 (missing sample datasets / EC2 catch-up)

Use when admin **Datasets** only shows knotweed (or other `tff-sample-data` folders never imported). One command:

```bash
python backend/manage.py seed_round_2 --owner <username>

# EC2 (rebuild first so /app/sample-data exists in the image)
docker compose -f docker-compose.prod.yml up --build -d
docker compose -f docker-compose.prod.yml exec backend python backend/manage.py seed_round_2 --owner <username>
```

This runs, in order:

1. `cleanup_seed_duplicates`
2. `seed_sample_projects --update`
3. `seed_sample_datasets --create-missing-projects`

Idempotent — safe to re-run; skips files already attached unless you add `--update-files`.

Expected result: **6 datasets**, **18 files**.

| Dataset title | Project slug |
|---------------|--------------|
| Knotweed Treatment Plot Outcomes | `knotweed-management-study` |
| Continuous Forest Inventory — Field Data & Manual | `forest-inventory-transect-study` |
| NYBG Breeding Bird Census Data | `breeding-bird-census` |
| Ten Tallest Plot Data | `acorn-planting` |
| Million Tree Plot — Plot 101-1 | `million-tree-plot` |
| Forest Soil Sampling & FEMC Analysis | `soil-monitoring` |

### EC2 / RDS (production)

```bash
cd ~/tff-website && git pull
docker compose -f docker-compose.prod.yml up --build -d

docker compose -f docker-compose.prod.yml exec backend python backend/manage.py cleanup_seed_duplicates
docker compose -f docker-compose.prod.yml exec backend python backend/manage.py seed_sample_projects --owner <username> --update   # only if metadata changed
docker compose -f docker-compose.prod.yml exec backend python backend/manage.py seed_sample_datasets --owner <username>            # only if files changed
```

---

## Canonical project slugs

### Research (`seed_sample_projects`)

| Short title (seed) | Slug |
|--------------------|------|
| CFI | `forest-inventory-transect-study` |
| Filling in the Gaps… | `filling-in-the-gaps` |
| Long-term Redback Salamander… | `redback-salamander-monitoring` |
| Citizen Science Phenology… | `citizen-science-phenology-monitoring` |
| Knotweed Management Study | `knotweed-management-study` |
| Macroinvertebrate Monitoring | `macroinvertebrate-monitoring` |

### Sample-data folders (`seed_sample_datasets`)

| Folder | Slug | Links to research project? |
|--------|------|----------------------------|
| `knotweed/` | `knotweed-management-study` | Yes |
| `CFI/` | `forest-inventory-transect-study` | Yes |
| `breeding bird census/` | `breeding-bird-census` | Data-only project |
| `acorn planting/` | `acorn-planting` | Data-only project |
| `million tree plot/` | `million-tree-plot` | Data-only project |
| `soil monitoring/` | `soil-monitoring` | Data-only project |

---

## Why duplicates happened (EC2, June 2026)

`Project.save()` used to **overwrite an explicit `slug` on create** with a slug generated from `short_title`. Example:

- Seed set `slug=filling-in-the-gaps` but `short_title` was the long Sandy title.
- DB row got `filling-in-the-gaps-plant-establishment-after-hurricane-sandy` instead.
- Next `seed_sample_projects --update` looked up `filling-in-the-gaps`, found nothing, and created **another** row (`-1`, `-2`, …).

**Fixes in repo:**

- `Project.save()` only auto-generates a slug when `slug` is empty.
- `cleanup_seed_duplicates` merges alias/` -1` / `-2` rows onto canonical slugs.
- `seed_sample_projects` consolidates before create/update.

**Wrong slugs cleanup knows about** (see `PROJECT_SLUG_ALIASES` in `seed_constants.py`):

- `filling-in-the-gaps-plant-establishment-after-hurricane-sandy` → `filling-in-the-gaps`
- `long-term-redback-salamander-monitoring` → `redback-salamander-monitoring`
- `acorn-planting-ten-tallest-method` → `acorn-planting`
- `annual-breeding-bird-census` → `breeding-bird-census`
- `million-tree-plot-monitoring` → `million-tree-plot`
- `forest-soil-monitoring` → `soil-monitoring`

Add new aliases there if a future seed typo produces a new wrong slug pattern.

---

## After seeding: public site

Admin list ≠ public site. In Django admin (or `/projects`), enable:

- **Shared publicly** on projects for `/research`
- **Expose on public API** on datasets (and files if needed) for `/data`

---

## Related files

- [`seed_sample_projects.py`](../backend/apps/datasets/management/commands/seed_sample_projects.py)
- [`seed_sample_datasets.py`](../backend/apps/datasets/management/commands/seed_sample_datasets.py)
- [`cleanup_seed_duplicates.py`](../backend/apps/datasets/management/commands/cleanup_seed_duplicates.py)
- [`seed_utils.py`](../backend/apps/datasets/seed_utils.py) — consolidate / merge logic
- Sample binaries: [`src/lib/data/tff-sample-data/`](../src/lib/data/tff-sample-data/)
