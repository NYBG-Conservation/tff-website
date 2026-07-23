# Welcome — Thain Family Forest Research Portal

**For:** External researchers with an NYBG portal account (`external_admin`)  
**Length:** ~2 pages, ~8 minutes
**Full reference:** [EXTERNAL_PARTNER_GUIDE.md](EXTERNAL_PARTNER_GUIDE.md)

---

## What this portal is

NYBG’s Thain Family Forest research portal is where approved researchers **register projects**, **link datasets**, and (when ready) surface them on the public **Research** and **Data** pages.

It is **not** the Living Collections / on-site research application. Approval to work in the Forest still goes through NYBG’s research process first.

---

## Your login

| Item | Notes |
|------|--------|
| **URL** | [Django admin on the NYBG API host](http://54.224.235.107:8000/admin/login/?next=/admin/)|
| **Username** | jwehr |
| **Password** | Provided over call |

If login fails: check username (not email), correct URL, and Caps Lock. Contact [afu@nybg.org](mailto:afu@nybg.org).

---

## What you can see and edit

You are an **external admin**. You can create and edit:

- Projects **you own**
- Projects where you are listed as a **manager**
- Datasets tied to those projects

You cannot see the rest of your institution's private records -- if you'd like the ability to view/manage all your organization's projects, you can requeste **superadmin** status.

---

## The workflow in one picture

```text
Research approval (NYBG) → Portal account
        ↓
Reserve Figshare DOI for the project
        ↓
Create Project in admin (include Figshare URL)
        ↓
Add Dataset(s) → link files (prefer Figshare URL)
        ↓
When ready: turn on public visibility flags (with NYBG if unsure)
```

**Figshare:** [How to reserve a DOI](https://info.figshare.com/user-guide/how-to-reserve-a-doi/)

---

## Important project fields

When you click **Datasets → Projects → Add**:

| Required | Why it matters |
|----------|----------------|
| **Short title** | Name on cards and lists |
| **Lead name** | Primary contact shown for the project |
| **Lead email** | Receives automated data-upload reminders |
| **Organization** | Your home institution (must match your account) |
| **Figshare item URL / reserved DOI** | Required when creating a project, unless you check **I plan to publish this data with my own DOI** |

**Strongly recommended:** Summary, Description, Start date; End date when the project will conclude (and then uncheck **Ongoing**).

**Slug**, owner, and some system flags are set for you—leave them alone.

---

## Datasets and files (short version)

1. Create a **Dataset** under your project (**Datasets → Datasets → Add**).
2. Put primary data on **Figshare** whenever you can.
3. In admin, attach either a small **upload** (≤ ~100 MB is fine) **or** an **External URL** (Figshare link). Over **1 GB** → external URL only.
4. Provide **exactly one** of: uploaded file **or** external URL — not both.

---

## Nothing is public until you say so

Admin drafts stay private until you enable flags:

| Public page | What to turn on |
|-------------|-----------------|
| `/research` project | Project → **Shared publicly** |
| `/data` dataset | Dataset → **Expose on public API** + status Active/Archived |
| `/data` downloads | Each file → **Expose on public API** |

When in doubt, leave flags **off** and ask [forest@nybg.org](mailto:forest@nybg.org).

---

## After your project ends

If the project has an **end date** (not ongoing) and no dataset file is linked yet, the lead email may get reminders at **30, 60, and 90 days**. Linking at least one file (upload or Figshare URL) stops the reminder queue.

So: reserve Figshare early, upload when you can, then link it in the portal.

---

## Your first-week checklist

- [ ] Log in once with username + password
- [ ] Reserve a Figshare DOI for your Forest project
- [ ] Create or finish your **Project** (required fields above)
- [ ] Add a **Dataset** shell linked to that project (even before files are ready)
- [ ] Read the full [External Partner Guide](EXTERNAL_PARTNER_GUIDE.md) if you feel you need more context (~15 minutes)
- [ ] Email [afu@nybg.org](mailto:afu@nybg.org with blockers (login, org name, Figshare, publishing)

---

## Feedback I'd love to have
- Do the processes of initializing a project and an associated dataset feel intuitive?
- Are there any other fields that you feel should be included, either required or optional, for project or dataset entries?
- If you had any questions, was it easy to find out the answer using the documentation?
- Overall compatibility with the research process, having to do with the practicality of using the portal

---

## Who to contact

**Forest program / portal help:** [afu@nybg.org](mailto:afu@nybg.org)

To discuss during the intro call: this one-pager, your username, and (if you have it) your Figshare item URL or questions about reserving one.

---

*Keep this sheet handy. The partner guide has field-by-field detail; this page is the map.*
