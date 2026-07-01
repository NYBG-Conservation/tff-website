# Overdue Data Alert Spec (v1)

## Goal

Automatically flag projects and notify lead researchers when a project passes its end date by 30 days and still has no uploaded data.

## Scope

- Add backend automation to detect overdue/no-data projects daily.
- Add project-level alert state to avoid duplicate email spam.
- Expose an overdue flag in project API payloads.
- Highlight overdue rows in the project dashboard UI.

Out of scope for v1:

- SMS/Slack notifications
- complex escalation chains
- arbitrary per-project SLA windows

## Business Rule

A project is considered **overdue for data upload** when all conditions are true:

- `project.ongoing == false`
- `project.end_date` is set
- `today >= project.end_date + 30 days`
- no qualifying data uploads exist (see definition below)

### Qualifying Upload Definition (v1)

For v1, a project is treated as having uploaded data if **either**:

- at least one `Dataset` exists linked to `Project`, or
- at least one `DatasetFile` exists under any linked dataset

Note:

- This is intentionally permissive to reduce false alarms during initial rollout.
- v2 can tighten to require `DatasetFile` only.

## Data Model Changes

Add an alert tracking model in `apps.datasets` (or a `notifications` app later):

- `ProjectAlert`
  - `project` FK -> `Project`
  - `alert_type` (`missing_data_overdue`)
  - `status` (`active`, `resolved`, `snoozed`)
  - `first_triggered_at` datetime
  - `last_evaluated_at` datetime
  - `last_emailed_at` datetime nullable
  - `resolved_at` datetime nullable
  - `resolution_note` text blank
  - unique constraint on (`project`, `alert_type`, `status='active'`) or equivalent enforcement

Rationale:

- Tracks lifecycle and prevents repeated "first alert" sends.
- Supports reminders and later admin actions.

## Scheduler + Command

Implement a management command:

- `python backend/manage.py check_overdue_project_uploads`

Command behavior:

1. Query candidate projects by date/ongoing status.
2. Determine if qualifying uploads exist.
3. For overdue/no-data projects:
  - create or update active `ProjectAlert`
  - send email if first trigger or reminder interval met
4. For projects no longer overdue/no-data:
  - mark active alert as resolved with timestamp

Scheduling:

- Run daily (cron, platform scheduler, or Celery Beat).
- Recommended run window: early morning local time.

## Reminder Cadence

v1 notification cadence:

- Send first email when project first becomes overdue/no-data.
- Send reminder every 7 days while unresolved.
- Stop sending when resolved.

## Email Spec

Recipient priority:

1. `Project.lead_email`
2. fallback to `Project.owner.email` (if present)

Optional CC (feature flag):

- delegated project managers with non-empty emails

Email subject:

- `[Action needed] Upload project data to Figshare: <short_title>`

Email body includes:

- project title
- end date
- **Figshare deposit URL** (`Project.figshare_doi_url`)
- link to [How to reserve a DOI in Figshare](https://info.figshare.com/user-guide/how-to-reserve-a-doi/)
- direct URL to Django admin project edit screen
- steps: upload to Figshare, then link files or external URL in a dataset

Reminder cadence unchanged (first email on trigger, then every 7 days).

## Figshare DOI requirement (project creation)

Every **new** project must include `figshare_doi_url` — the Figshare item URL or reserved DOI link.

- Validated in API (`ProjectSerializer`) and Django admin (`ProjectAdminForm`)
- Accepted hosts: `figshare.com` (including institutional subdomains), `doi.org`, `dx.doi.org`
- Legacy seeded projects may have a blank value until backfilled
- Guide URL configurable via `FIGSHARE_DOI_GUIDE_URL` (default: Figshare user guide)

Researchers reserve the DOI **before** data collection, upload files to Figshare when ready, and link deposits from the project's dataset records on this site.

## API Changes

Extend project serializer response with computed fields:

- `is_overdue_missing_data: boolean`
- `overdue_days: number` (0 when not overdue)
- `active_alert_id: number | null`
- `last_alert_emailed_at: datetime | null`

No breaking changes to request payloads.

## UI Changes

In `src/routes/projects/+page.svelte`:

- highlight rows where `is_overdue_missing_data` is true (red-tinted background/border)
- show badge text: `Data overdue`
- optional tooltip/details:
  - overdue days
  - last email sent timestamp

Upload governance text remains unchanged.

## Permission Behavior

- Existing role constraints remain.
- Overdue flags are visible only for projects the user can already view.
- Internal NYBG admins continue to see NYBG-scoped projects only.

## Edge Cases

- `ongoing=true`: never flagged, regardless of end date.
- no `end_date`: never flagged.
- timezone: use Django timezone-aware `now()` and compare by date.
- no reachable recipient email: create alert but skip send; log warning.
- project with external URL only and no dataset records: still flagged under v1 rule.

## Configuration

Add env-configurable settings:

- `PROJECT_OVERDUE_DAYS=30`
- `PROJECT_ALERT_REMINDER_DAYS=7`
- email backend settings (`EMAIL_BACKEND`, SMTP host/user/pass, default from email)

## Observability

Command should log summary counts:

- checked projects
- newly flagged
- reminders sent
- resolved alerts
- skipped due to missing recipient

Optional: persist run metrics later.

## Test Plan

Backend tests:

- becomes overdue exactly on day 30 threshold
- not flagged before threshold
- ongoing project excluded
- resolved when dataset added
- first email sent once, reminders follow cadence
- no duplicate active alerts

API tests:

- project payload includes overdue fields
- values reflect alert and upload state

UI tests:

- overdue row styling appears when flag true
- non-overdue rows unaffected

## Rollout Plan

1. Add model + migration for `ProjectAlert`.
2. Implement overdue evaluation service + management command.
3. Configure scheduler in deployment environment.
4. Add project API computed fields.
5. Add UI row highlight + badge.
6. Enable in staging with test dates/emails.
7. Promote to production.

## Future Extensions (Post-v1)

- Admin snooze/acknowledge controls.
- Configurable thresholds by project type.
- Distinguish "metadata created" vs "actual file upload".
- Multi-channel notifications (Slack/Teams).