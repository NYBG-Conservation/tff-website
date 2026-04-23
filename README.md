# NYBG Urban Conservation Resource Hub

Annie Fu (afu@nybg.org)

### Development began January 2026

## Backend

A Django + Postgres backend scaffold now lives in `backend/` for researcher/admin dataset workflows.

- Setup guide: `backend/README.md`
- API contract: `backend/API_CONTRACT.md`

### Minimal startup

Install Python dependencies, run migrations, and start the server:

- `pip install -r backend/requirements.txt`
- `python backend/manage.py migrate`
- `python backend/manage.py runserver`

### Minimal architecture

The Svelte frontend calls Django REST endpoints under `/api/...`. Django handles auth, permissions, and dataset validation, and Postgres stores users, organizations, datasets, metadata definitions/values, and file version records.