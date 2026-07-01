# Overdue Data Alert Spec (v2)

## Goal

Automatically notify project leads when a **concluded** project (discrete `end_date`, not ongoing) still has no linked dataset files for its Figshare deposit — at **30, 60, and 90 days** after the end date. At **90 days**, flag the project for **manual NYBG outreach** if data is still missing.

## Business rule

A project enters the alert pipeline when:

- `project.ongoing == false`
- `project.end_date` is set
- `today >= project.end_date + 30 days`
- **no qualifying data deposit** exists (see below)

### Qualifying data deposit

A project is treated as compliant when it has at least one **linked `DatasetFile`** under any project dataset, where either:

- a file was uploaded directly, or
- `external_url` points to the project's Figshare deposit (or another `figshare.com` / `doi.org` URL)

Researchers reserve `figshare_doi_url` at project registration, upload to Figshare when ready, then link files from Django admin.

## Milestone emails

| Days after `end_date` | Action |
|----------------------|--------|
| **30** | First automated email to project lead |
| **60** | Second reminder email |
| **90** | Final automated email + **manual outreach flag** |

- One milestone email per daily command run (no duplicate sends).
- If the cron was down, the next run sends the **oldest unsent** milestone (catch-up one at a time).
- Ongoing projects and projects without `end_date` are **never** flagged.

## Manual outreach (90 days)

When `today >= end_date + 90 days` and data is still missing:

- `Project.manual_outreach_required = true`
- `Project.manual_outreach_at` set
- Active `ProjectAlert` with `alert_type = manual_outreach_required`

NYBG staff use Django admin:

- Filter projects by **Manual outreach required**
- Review Alerts inline on the project
- Contact the lead directly; clear the flag when resolved by linking dataset files (automatic) or manually unchecking after outreach

## Scheduler + command

```bash
python backend/manage.py check_overdue_project_uploads
```

Run **daily** (cron on EC2). On production:

```bash
docker compose -f docker-compose.prod.yml exec backend python backend/manage.py check_overdue_project_uploads
```

When data is linked, active `missing_data_overdue` and `manual_outreach_required` alerts are **resolved** automatically.

## Configuration

| Setting | Default | Purpose |
|---------|---------|---------|
| `PROJECT_ALERT_MILESTONE_DAYS` | `30,60,90` | Comma-separated reminder days after `end_date` |
| `PROJECT_MANUAL_OUTREACH_DAY` | `90` | Day to flag manual outreach (should match last milestone) |
| `DEFAULT_FROM_EMAIL` | — | Sender for milestone emails |
| `DJANGO_API_PUBLIC_URL` | — | Admin links in email bodies |

Legacy `PROJECT_OVERDUE_DAYS` / `PROJECT_ALERT_REMINDER_DAYS` are superseded by milestone days (no more every-7-day reminders).

## API fields (`ProjectSerializer`)

- `is_overdue_missing_data`
- `overdue_days` (days past first milestone)
- `days_since_project_end`
- `manual_outreach_required`
- `manual_outreach_at`
- `emailed_milestones` (e.g. `[30, 60]`)
- `active_alert_id`, `last_alert_emailed_at`

## Data model

- **`ProjectAlert`**: `missing_data_overdue`, `manual_outreach_required`; `emailed_milestones` JSON list
- **`Project`**: `manual_outreach_required`, `manual_outreach_at`

## Figshare DOI requirement

Every new project requires `figshare_doi_url`. Guide: [How to reserve a DOI in Figshare](https://info.figshare.com/user-guide/how-to-reserve-a-doi/).

---

## v1 history (superseded)

v1 used a single 30-day threshold and repeated emails every 7 days. v2 replaces that with fixed 30/60/90 milestones and the manual outreach flag.