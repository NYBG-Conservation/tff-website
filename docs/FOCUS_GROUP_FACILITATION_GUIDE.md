# Focus group facilitation guide

**Thain Family Forest research portal**  
**Audience:** Partner researchers who have tried logging in, creating a project, and adding data  
**Length:** ~45 minutes (can compress to 30)  
**Facilitator notes:** Keep this light. Recap is 2 minutes, then let them talk. Prompt, don’t defend.

---

## Agenda

| Time | Block |
|------|--------|
| 0–5 | Intros and purpose |
| 5–8 | Recap: public site vs portal |
| 8–28 | Walk the workflow (project → data → publications) |
| 28–35 | Organization, docs, and overall feedback |
| 35–45 | What’s next + questions |

If short on time: skip publications, keep one prompt per workflow step, and still hit “what to improve” and “what’s next.”

---

## 1. Intros (5 min)

Welcome people and set the tone:

- This is feedback on the **research portal**, not a training session.
- There are no wrong answers. Rough edges are useful.
- We’re looking for what was confusing, missing, or extra — not a product demo.

**Round of intros (30–45 seconds each):**

- Name, affiliation, and what kind of Forest work you do
- Did you get as far as: login / project / dataset / file / publication?

**Optional icebreaker:** One word for first login — *smooth, confusing, fine, unfinished.*

---

## 2. Recap: how the website is structured (3 min)

Keep this visual and short. Two layers, not two websites they have to “choose.”

```text
Public website (frontend)
  Home, Visit, Research, Data, Education…
  Anyone can browse. Research and Data pull live from the portal.

Research portal (backend / Django admin)
  Where you log in after NYBG approval.
  Create and manage Projects, project files, optional dataset catalog entries, and publications.
  Nothing appears on the public site until visibility flags are turned on.
```

**What to say:**

- The **public site** is the forest hub visitors see (`/research`, `/data`).
- The **admin portal** is where approved researchers catalog a project and attach data.
- Typical path: apply → get an account → create/finish a **Project** (Figshare DOI) → add **Project files** (typed: dataset, presentation, methods, etc.) → optionally add a **Dataset catalog** row for `/data` → add **publications** when you have them → NYBG helps decide when to make it public.

Invite a 30-second check: *Does that match how you understood it going in?*

---

## 3. Workflow walkthrough (20 min)

Go step by step. For each step: one sentence of what we intended, then questions. Don’t re-teach the whole form.

### A. Getting in and finding your way

- Was it clear where to log in, and that you use a **username** (not email)?
- Once inside, was it obvious where **Projects** vs **Project files** vs **Dataset catalog** lived?
- **Interface:** Was it difficult to tell what information was required for which fields? Could you navigate intuitively, or did you hunt?

### B. Creating a project

Intended path: **Project admin → Projects → Add** (or finish the project created from your application). Required: short title, lead name/email, organization, Figshare URL (unless you plan to use your own DOI).

- What felt obvious vs. what made you pause?
- Figshare DOI before (or as) you create the project — did that fit your real research process?
- Any fields you wanted that weren’t there? Any that felt unnecessary?
- After saving, did you understand what had been created (and what still needed to happen)?

### C. Adding project files

Intended path: on the **Project** form, use the **Project files** inline. Choose a file kind (peer-reviewed, dataset, presentation, extramural documents/methods/summary, public infographic, or other), then attach a file **or** a Figshare/external URL (not both). Prefer Figshare for data; large files should be a URL, not a direct upload.

- Was choosing a **file kind** clear?
- **Uploads:** Any issues with file uploads, formats, or sizes? Did “upload vs paste a URL” make sense?
- Did you know drafts stay private until someone turns on public flags?
- Optional: if you also tried **Dataset catalog** for `/data`, was that distinction clear?

### D. Adding publications

- Did you find where publications live (on the project, and/or on a dataset)?
- Was the citation / year / DOI / URL set enough, or too much?
- Would you expect publications to show on `/research` automatically, or only after a flag?

---

## 4. Cross-cutting questions (7 min)

Use whatever wasn’t already answered in the walkthrough. Skip a prompt if the room already covered it.

### Documentation

- Did you consult the documentation at any point?
- Did you find the answers you were looking for?
- Would you rather it be more concise, more detailed, or easier to find at the moment of need (e.g. next to a field)?

### Organization management

- Were you able to see other users or projects from your organization?
- When adding future members, what would you like to take into account? (who can view vs edit, how colleagues get accounts, team members vs a new login)

### General

- What could be improved about the system overall?
- Any additional features or functionality you hope to see?
- Anything that would make this fit better into how you actually run a study?

---

## 5. What’s next + questions (10 min)

**You talk (2–3 min), then open the floor.**

Suggested talking points (adjust to current plans):

- This portal is still in a **focus-group / staging** phase. Feedback from this session will shape the next round of edits.
- **Public launch:** the public Research and Data pages will show projects and datasets only when records are marked visible. Until then, work in admin stays private.
- After launch, expect: accounts for approved researchers, Figshare as the home for data, and light NYBG follow-up if a concluded project still has no linked files (reminders at 30 / 60 / 90 / 120 days).
- Support: [afu@nybg.org](mailto:afu@nybg.org) / [forest@nybg.org](mailto:forest@nybg.org).

**Close with:**

- What would you need in order to actually use this for a real project?
- Any questions about timeline, access, or what goes public?

Thank people. Note who offered to send a follow-up example (a form screenshot, a failed upload, a missing field).

---

## Facilitator cheat sheet

| If they say… | Follow up with… |
|--------------|-----------------|
| “I didn’t know what to put in X” | Was that a labeling problem, missing help text, or unclear why it mattered? |
| “I didn’t use the docs” | Would in-form hints have been enough? |
| “Upload failed / was slow” | Size, format, or “should this have been a Figshare link?” |
| “I couldn’t see my colleague’s project” | Same organization on both accounts? View-only vs edit is expected. |
| Silence | Ask the quietest person: “Where did you get stuck first?” |

**Don’t need to cover live:** alerts/snooze, roles matrix, deployment, or turning on public flags unless they bring it up.
