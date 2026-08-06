# First External Admin Onboarding — 30-Minute Call

**Audience:** NYBG facilitator (you) + first external `external_admin` researcher  
**Goal:** Researcher can log in, understands the portal’s purpose, creates (or walks through) one project, and knows what to do next and where to get help.  
**Companion handout:** [EXTERNAL_ADMIN_INTRO.md](EXTERNAL_ADMIN_INTRO.md) (send 24 hours before the call + password via separate channel)

---

## Before the call (you — ~15–20 min prep)

| Done? | Task |
|-------|------|
| ☐ | Account exists: Django user + User profile with role `external_admin` and **Organization** linked (saving the profile auto-sets Staff + Project/Dataset group permissions) |
| ☐ | If admin still shows “can’t view or edit anything”, run `sync_role_groups` on EC2 once after deploy |
| ☐ | Password set; send **username + admin URL** and **password** on **separate** channels (email + call/text) |
| ☐ | Organization record already exists with correct name |
| ☐ | Confirm they have (or can get) a Figshare account; share [Reserve a DOI](https://info.figshare.com/user-guide/how-to-reserve-a-doi/) |
| ☐ | Send [EXTERNAL_ADMIN_INTRO.md](EXTERNAL_ADMIN_INTRO.md) + [EXTERNAL_PARTNER_GUIDE.md](EXTERNAL_PARTNER_GUIDE.md) link |
| ☐ | Optional: draft / demo project template (short title, lead email) ready so you don’t invent fields live |
| ☐ | Have admin open in a second window (you logged in as NYBG staff) in case you need to fix org/role |
| ☐ | Confirm research approval status (in-site application / Forest approval) so the session isn’t blocked on process |

**Do not try to cover the full partner guide in 30 minutes.** Point to it; live practice beats reading.

---

## Agenda (30 minutes)

| Time | Block | Who drives | Outcome |
|------|-------|------------|---------|
| **0–3** | Welcome + purpose | You | Shared mental model: catalog + link data, not replace research approval |
| **3–8** | Login + orientation | Researcher (you coach) | In admin; knows username ≠ email; sees only their records |
| **8–14** | Figshare + required fields | You → researcher | Understands DOI-before-fieldwork; knows project must have Figshare URL |
| **14–24** | Live create (or edit) one Project | Researcher | Draft project saved (or carefully walk draft then delete if preferred) |
| **24–28** | Datasets, files, public flags | You (demo-lite) | Knows next steps; won’t accidentally publish |
| **28–30** | Close + next steps | You | Clear homework + forest@nybg.org |

### Minute-by-minute talking points

#### 0–3 — Welcome + purpose
- “This portal is how we catalog approved Forest research and connect the public `/research` and `/data` pages to real projects and files.”
- “It does **not** replace the Living Collections / on-site research application.”
- “Your role is **external admin**: you manage **your** projects and anything you’re added to as a manager—not other institutions.”

#### 3–8 — Login + orientation
- Researcher opens the admin URL you provided.
- Login with **username** (not email). If failure: check caps, correct host, staff flag.
- Tour (90 seconds): **Datasets → Projects**, **Datasets → Datasets**. Ignore unrelated admin modules.
- Show empty or filtered list: “You only see what you own/manage—that’s intentional.”

#### 8–14 — Figshare + required project fields
- “Before (or as) you create a project: reserve a DOI in Figshare and keep that item URL.”
- Required on create: **Short title**, **Lead name**, **Lead email**, **Organization**, **Figshare item URL**.
- Lead email = where 30/60/90-day upload reminders go after a project ends—use a monitored inbox.
- Ongoing vs end date: if the project will end, set an end date and leave Ongoing unchecked when concluded.

#### 14–24 — Live project create (core of the call)
Researcher shares screen if possible.

Suggested path:
1. **Projects → Add**
2. Fill required fields + short **Summary** (1–2 sentences)
3. Organization = their institution (same as profile)
4. Paste Figshare URL (or open Figshare tip tab if not reserved yet—then save after they have URL)
5. **Save**
6. Show slug is auto; show where they’d add managers later

If they aren’t ready for a real project:
- Create clearly labeled **Draft/test** project they can delete later, **or** you drive with their fields while they watch, then they repeat alone as homework.

**Avoid:** publications, custom metadata schemas, uploads >100 MB, public flags—on this call.

#### 24–28 — Datasets / files / public (light touch)
- Project → later add **Dataset(s)** linked to that project.
- Prefer: data lives on **Figshare**; in admin, attach as **External URL** (required if >1 GB).
- Public site is **off by default**. Enabling **Shared publicly** / **Expose on public API** makes things appear on the website—ask NYBG if unsure.
- Mentions only: after a concluded end date, reminders start if no dataset file is linked.

#### 28–30 — Close
- Homework (pick 1–2): finish Figshare DOI if missing; complete project description; add first dataset shell; send any blockers to forest@nybg.org
- Confirm they’ve received the intro + full guide
- Book optional 15‑min “office hours” follow-up in 1–2 weeks if first researcher / first real project

---

## How the call should feel

### Your job
- **Reassure:** admin UIs look busy; they only need Projects / Datasets.
- **Co-pilot, don’t take over:** they drive the mouse for the save.
- **One success:** a saved project (or a clear path + Figshare reservation booked).
- **Park deep questions** (“Can we bulk import?”) → email after, don’t derail the live create.

### Their job
- Share screen when creating.
- Say aloud what they expect each field means (you correct misconceptions in real time).
- Leave knowing the **admin URL**, **username**, **where the guide is**, and **one next action**.

### Tone / norms for a first external admin
- This person is a **guinea pig**—say that kindly: “You’re our first partner on the new portal; friction is feedback.”
- Expect Figshare or DOE/org IT delays; offer to leave the call with a Figshare tab + checklist, not a forced incomplete save.
- Do **not** ask them to toggle public visibility on a live call without NYBG content review.

### If something goes wrong

| Problem | Fix |
|---------|-----|
| Can’t log in | Username not email; wrong URL; password reset via `changepassword` on EC2 / you reset; confirm `is_staff` |
| Org missing / wrong | You add Organization in admin; set on User profile |
| Sees no Projects / empty world | Expected if they own nothing yet—create first project together |
| Figshare URL validation error | Must be figshare.com or doi.org style link |
| Panic about public site | Show flags default off; “Nothing publishes until you (and we) intend it” |
| Out of time | Stop after project fields explained; assign Figshare + create as homework; send follow-up email same day |

### Same-day follow-up email (template)

```text
Subject: TFF portal — next steps after today’s intro

Hi [Name],

Thanks for joining. Quick recap:

• Admin login: [URL] — use username [username] (not email)
• Role: external admin — your projects and datasets only
• Required for every new project: short title, lead name/email, organization, Figshare item URL
• Full guide: [link to EXTERNAL_PARTNER_GUIDE]
• One-pager: [link to EXTERNAL_ADMIN_INTRO]

Your next step: [e.g. reserve Figshare DOI / finish project description / add dataset]

Questions → forest@nybg.org

[Your name]
```

---

## Optional stretch (only if call finishes early)

- Add team member by username  
- Create empty dataset linked to project  
- Show `/research` and `/data` public pages so they see end-user destination  

---

## Facilitator checklist after the call

| Done? | Task |
|-------|------|
| ☐ | Same-day recap email sent |
| ☐ | Note any UI confusion (feed into guide updates) |
| ☐ | Confirm account org/role still correct |
| ☐ | If they created a test project, agree delete-by date or rename to real |
| ☐ | Schedule optional follow-up if needed |
