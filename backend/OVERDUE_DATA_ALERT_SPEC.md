# Overdue Data Alert Spec (v3)

## Goal

Automatically notify project leads when a **concluded** project (discrete `end_date`, not ongoing) still has no linked dataset files for its Figshare deposit — at **30, 60, 90, and 120 days** after the end date. At **60 days**, flag the project for **manual NYBG outreach** if data is still missing.

Follow-up status and alert timeline are visible to **NYBG internal superadmins only**. Alerts are system-generated; superadmins may **snooze** / **unsnooze**, not freely edit rows.

## Business rule

A project enters the alert pipeline when:

- `project.ongoing == false`
- `project.end_date` is set
- `today >= project.end_date + 30 days`
- **no qualifying data deposit** exists (see below)
- the project is **not snoozed**

### Qualifying data deposit

A project is treated as compliant when it has at least one **linked `DatasetFile`** under any project dataset, where either:

- a file was uploaded directly, or
- `external_url` points to the project's Figshare deposit (or another `figshare.com` / `doi.org` URL)

Researchers reserve `figshare_doi_url` at project registration, upload to Figshare when ready, then link files from Django admin.

## Milestone emails

| Days after `end_date` | Action |
|----------------------|--------|
| **30** | First automated email to project lead |
| **60** | Second reminder email + **manual outreach flag** |
| **90** | Third reminder email |
| **120** | Final automated email |

- One milestone email per daily command run (no duplicate sends).
- If the cron was down, the next run sends the **oldest unsent** milestone (catch-up one at a time).
- Ongoing projects and projects without `end_date` are **never** flagged.
- **Snoozed** projects skip further emails and clear the follow-up flag until unsnoozed or data is linked.

## Manual outreach (60 days)

When `today >= end_date + 60 days`, data is still missing, and the project is not snoozed:

- `Project.manual_outreach_required = true`
- `Project.manual_outreach_at` set
- Active `ProjectAlert` with `alert_type = manual_outreach_required`

These fields stay in sync with the alert timeline (cleared on data link or snooze).

NYBG **internal superadmins** use Django admin:

- Filter projects by **Manual outreach required**
- Review **Project alerts** (read-only timeline: milestones emailed, timestamps, status)
- **Snooze** to pause emails and clear the follow-up flag (marks outreach as handled for now)
- **Unsnooze** to resume the automated pipeline

Other roles do not see the follow-up fields, alert inline, or Project alerts module.

## Scheduler + command

```bash
python backend/manage.py check_overdue_project_uploads
```

Run **daily** (cron on EC2). On production:

```bash
docker compose -f docker-compose.prod.yml exec backend python backend/manage.py check_overdue_project_uploads
```

When data is linked, active/snoozed `missing_data_overdue` and `manual_outreach_required` alerts are **resolved** automatically.

## Configuration

| Setting | Default | Purpose |
|---------|---------|---------|
| `PROJECT_ALERT_MILESTONE_DAYS` | `30,60,90,120` | Comma-separated reminder days after `end_date` |
| `PROJECT_MANUAL_OUTREACH_DAY` | `60` | Day to flag manual outreach (must be one of the milestones) |
| `DEFAULT_FROM_EMAIL` | `forest@nybg.org` | Sender for milestone emails |
| `DJANGO_API_PUBLIC_URL` | — | Admin links in email bodies |

Legacy `PROJECT_OVERDUE_DAYS` / `PROJECT_ALERT_REMINDER_DAYS` are superseded by milestone days.

## API fields (`ProjectSerializer`)

Exposed only to **internal superadmins**:

- `is_overdue_missing_data`
- `overdue_days` (days past first milestone)
- `days_since_project_end`
- `manual_outreach_required`
- `manual_outreach_at`
- `active_alert_id`
- `last_alert_emailed_at`
- `emailed_milestones`

## Data model notes

- **`ProjectAlert`**: `missing_data_overdue`, `manual_outreach_required`; statuses `active` / `snoozed` / `resolved`; `emailed_milestones` JSON list
- **`Project`**: `manual_outreach_required`, `manual_outreach_at` (system-owned; not manually editable)
