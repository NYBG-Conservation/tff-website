# External Partner Guide — Thain Family Forest Research Portal

**Audience:** Partner institutions and visiting researchers who have been given an account to register and manage research projects and datasets for work in the Thain Family Forest.

**Management URL:** Django admin on the NYBG API host (e.g. `http://54.224.235.107:8000/admin/login/?next=/admin/`). NYBG staff will provide your login URL and credentials.

---

## Table of contents

1. [Before you start](#1-before-you-start)
2. [Getting an account](#2-getting-an-account)
3. [Your role and what you can edit](#3-your-role-and-what-you-can-edit)
4. [Workflow overview](#4-workflow-overview)
5. [Project metadata — required vs optional](#5-project-metadata--required-vs-optional)
6. [Dataset metadata — required vs optional](#6-dataset-metadata--required-vs-optional)
7. [Dataset files and upload policy](#7-dataset-files-and-upload-policy)
8. [Publications](#8-publications)
9. [Making content visible on the public website](#9-making-content-visible-on-the-public-website)
10. [Data deposit reminders (30 / 60 / 90 days)](#10-data-deposit-reminders-30--60--90-days)
11. [Checklist: new project](#11-checklist-new-project)
12. [Support and links](#12-support-and-links)

---

## 1. Before you start

Conducting research in the Thain Family Forest requires NYBG approval. If you have not already applied:

- Complete the [NYBG Living Collections Research Application](https://survey123.arcgis.com/share/512cee2ac8f444008ec5f5ddeae69072) (submit at least two weeks before your start date).
- Review on-site agreements and resources on the public [Research](/research) page.

This portal is for **cataloging approved projects and linking data** after you are set up with an account. It does not replace the formal research application process.

---

## 2. Getting an account

Accounts are **created by NYBG staff** — there is no public self-registration.

NYBG will:

1. Create a Django user (username + password) for you or your team lead.
2. Assign your **organization** (your home institution in the system).
3. Assign a **role** (see below).

You will log in at the Django admin URL provided by NYBG. Use your **username** (not email) to sign in.

If you need a colleague to edit your projects, the project **owner** can add them as a **project manager** (by username), or ask NYBG to create an account for them.

**Contact:** [forest@nybg.org](mailto:forest@nybg.org)

---

## 3. Your role and what you can edit

| Role | Typical partner use | What you see | What you can edit |
|------|---------------------|--------------|-------------------|
| `external_admin` | Individual researcher | Projects and datasets you **own**, plus projects where you are a **delegated manager** | Those records only |
| `external_superadmin` | Partner institution lead | All projects and datasets for your **organization** | All records in your organization |

You cannot see or edit other institutions’ records. NYBG internal staff manage cross-institution oversight.

---

## 4. Workflow overview

```text
1. Apply for on-site research (Survey123) → NYBG approval
2. Receive portal account from NYBG
3. Reserve a Figshare DOI for your project (before field work)
4. Create Project in Django admin (include Figshare URL)
5. Add Dataset(s) under the project
6. Upload data to Figshare; link files in the dataset (upload or external URL)
7. When ready for the public site: enable visibility flags (see §9)
8. When project concludes: set end date, uncheck Ongoing → automated reminders if data not linked
```

**Figshare DOI guide:** [How to reserve a DOI in Figshare](https://info.figshare.com/user-guide/how-to-reserve-a-doi/)

---

## 5. Project metadata — required vs optional

In Django admin: **Datasets → Projects → Add**.

### Required when creating a project

| Field | Notes |
|-------|--------|
| **Short title** | Display name on research cards and admin lists. Max 255 characters. |
| **Lead name** | Primary project lead (display name). |
| **Lead email** | Receives automated data-upload reminders. Use a monitored address. |
| **Organization** | Your home institution. Must match the org on your user profile for external roles. |
| **Figshare item URL / reserved DOI** | URL from Figshare or `doi.org` for this project’s data deposit. **Required on every new project** unless you check **Plans own DOI**. |

### Strongly recommended

| Field | Notes |
|-------|--------|
| **Summary** | Short teaser on the public research project card (if published). |
| **Description** | Longer text for the project detail modal. Separate paragraphs with a blank line. |
| **Start date** | When field work or data collection began. |
| **End date** | Set when the project has a **discrete conclusion**. Required for the 30/60/90-day upload reminder schedule (see §10). |
| **Ongoing** | Check only if the project has **no fixed end date**. If ongoing, leave **End date** empty. |
| **Plans own DOI** | Check if you will publish data under your own DOI (journal / Dryad / Zenodo, etc.) instead of reserving Figshare first. Figshare URL then becomes optional. |
| **Institutional partners** | List of partner org names (shown on the public site if published). |

### Optional

| Field | Notes |
|-------|--------|
| **Full title** | Formal project title if different from short title. |
| **External URL** | Project website, grant page, or other reference link. |
| **Collection frequency** | Free text (e.g. `annual`, `seasonal`). |
| **Update frequency** | How often you expect to add or refresh data. |
| **Last updated note** | Internal note on recent changes. |
| **Shared publicly** | Off by default. Turn on when NYBG agrees the project should appear on [/research](https://www.nybg.org) (see §9). |

### Set automatically (do not edit)

| Field | Notes |
|-------|--------|
| **Slug** | Auto-generated from short title (used in URLs). Read-only. |
| **Owner** | Your user account (for external partners). |
| **Manual outreach required / at** | Set by the system after 90 days without linked data. |
| **Created / updated timestamps** | System-managed. |

### Validation rules

- **End date** cannot be before **start date**.
- If **Ongoing** is checked, **End date** must be empty.
- **Figshare URL** must be a valid `figshare.com` or `doi.org` link when provided. On create it is required unless **Plans own DOI** is checked.

---

## 6. Dataset metadata — required vs optional

Create datasets under **Datasets → Datasets → Add**, linked to your project.

### Required

| Field | Notes |
|-------|--------|
| **Title** | Dataset name shown on [/data](https://www.nybg.org). |
| **Cadence** | `Annual`, `One off`, or `Continuous`. |
| **Organization** | Usually your home institution (same as the project). |
| **Project** | Link to the parent research project. |

### Optional (with defaults)

| Field | Default | Notes |
|-------|---------|--------|
| **Description** | empty | Shown in expanded row on `/data`. |
| **Status** | `Draft` | Use `Active` when ready; `Archived` when complete. Only **Active** and **Archived** appear on the public site. |
| **Data type** | `Tabular` | Also: Geospatial, Image, Sensor time series, Biodiversity observation, Document archive. |
| **Expose on public API** | off | Must be on for public `/data` listing (see §9). |
| **Additional research partners** | empty | JSON list of partner names. |
| **Paper links** | empty | URLs to related publications. |
| **Data collection start / end** | empty | Optional date range for this dataset. |
| **Projected project end date** | empty | Optional planning field. |

### Metadata schema (optional, per dataset)

You may define **metadata fields** (schema) and **metadata values** for structured attributes (e.g. plot ID, units, survey year). Each field has:

| Property | Required? |
|----------|-----------|
| Key, label, field type | Yes, if you add custom fields |
| Unit | Optional |
| Required (per field) | Optional; default false |
| Allowed values | Optional; only for enum fields |

Field types: Text, Long text, Number, Integer, Boolean, Date, Datetime, Enum, URL.

---

## 7. Dataset files and upload policy

Each dataset can have **files** attached in the **Files** inline when editing a dataset.

### Per file

| Field | Required? | Notes |
|-------|-----------|--------|
| **Uploaded file** *or* **External URL** | One required | Provide exactly one — not both. |
| **File name** | Auto-filled if omitted | Shown on the public data page (extension used for file type label). |
| **File kind** | Optional | Primary data, Documentation, Code, Derived output, Image/media, Other. |
| **Expose on public API** | Optional | Must be on for public download/listing on `/data`. |
| **Notes** | Optional | Internal context. |

### Upload size policy

| Size | Policy |
|------|--------|
| **≤ 100 MB** | Direct upload in admin is fine. |
| **100 MB – 1 GB** | Upload allowed; **linking** (external URL) is preferred. |
| **> 1 GB** | **External URL required** — host on Figshare and paste the Figshare URL. |

**Recommended workflow:** Upload primary data to your project’s **Figshare deposit**, then add a dataset file row with the Figshare URL as **External URL**.

Public file downloads on the website are **desktop only** (large files).

---

## 8. Publications

Add under **Project publications** (inline on a project, or standalone in admin).

| Field | Required? | Notes |
|-------|-----------|--------|
| **Citation** | Yes | Formatted citation; basic HTML (e.g. `<em>`) allowed. |
| **Project** | Optional | Link to project; leave blank only for site-wide NYBG publications. |
| **Title** | Optional | Short label. |
| **Publication year** | Optional | |
| **DOI** | Optional | |
| **URL** | Optional | Link to paper. |
| **Featured** | Optional | Highlights in “Selected publications” on `/research`. |
| **Expose on public API** | Optional | Must be on to appear on `/research`. |

---

## 9. Making content visible on the public website

Admin changes are **not** public until visibility flags are set.

| To appear on… | Set on… | Flag |
|---------------|---------|------|
| `/research` project cards | Project | **Shared publicly** |
| `/research` publications | Project publication | **Expose on public API** |
| `/data` dataset rows | Dataset | **Expose on public API** + status **Active** or **Archived** |
| `/data` file downloads | Dataset file | **Expose on public API** |

NYBG may review before you enable public flags. Contact [forest@nybg.org](mailto:forest@nybg.org) if unsure.

---

## 10. Data deposit reminders (30 / 60 / 90 days)

For projects with a **fixed end date** (not ongoing):

| Days after end date | What happens |
|---------------------|--------------|
| **30** | First email to **lead email** — upload to Figshare and link files |
| **60** | Second reminder |
| **90** | Final reminder; project flagged **Manual outreach required** for NYBG staff follow-up |

Reminders stop when at least one **dataset file** is linked (upload or Figshare/external URL).

**To stay out of the reminder queue:**

1. Reserve Figshare at project creation (`figshare_doi_url`).
2. Upload data to Figshare when ready.
3. Create a dataset and attach files or paste the Figshare URL.
4. For concluded projects, set **End date** and uncheck **Ongoing**.

---

## 11. Checklist: new project

- [ ] Research application approved by NYBG
- [ ] Portal account received; can log into Django admin
- [ ] [Figshare DOI reserved](https://info.figshare.com/user-guide/how-to-reserve-a-doi/) for this project
- [ ] **Project** created with short title, lead name/email, organization, Figshare URL
- [ ] Summary and description drafted (for eventual public use)
- [ ] Start date set; end date set if project is not ongoing
- [ ] **Dataset(s)** created and linked to the project
- [ ] Files uploaded to Figshare and linked in the dataset (or direct upload ≤ 100 MB)
- [ ] Public visibility flags set only when ready (§9)

---

## 12. Support and links

| Resource | Link |
|----------|------|
| Forest program contact | [forest@nybg.org](mailto:forest@nybg.org) |
| Research application | [Survey123 application](https://survey123.arcgis.com/share/512cee2ac8f444008ec5f5ddeae69072) |
| Public research page | `/research` on the TFF website |
| Public data catalog | `/data` on the TFF website |
| Figshare DOI guide | [info.figshare.com — Reserve a DOI](https://info.figshare.com/user-guide/how-to-reserve-a-doi/) |
| Forest program plan (PDF) | [Thain Family Forest Program 2008–2025](https://www.nybg.org/content/uploads/2017/04/Forest-Plan-2016.pdf) |
| API reference (technical) | [backend/API_CONTRACT.md](../backend/API_CONTRACT.md) |

---

*This document reflects the current Django data model and validation rules. If admin labels differ slightly from field names here, use the in-admin help text and contact NYBG with questions.*
