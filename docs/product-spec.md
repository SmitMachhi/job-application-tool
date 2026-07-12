# Job Application Command Center — Product Spec

## Product goal

Build a simple local-first app that removes the worst parts of job searching:

1. The user should not have to visit job boards manually every day.
2. Relevant jobs should appear in an Excel workbook and dashboard.
3. Each job should include tailored resume material and a cover letter draft.
4. The user should be able to open the apply link and apply immediately.
5. Follow-ups should not be forgotten.
6. Private resume/profile data must stay local and encrypted where stored.

## Target user

General job seeker, starting with data analyst roles.

Initial target geography:

- GTA
- British Columbia
- Halifax
- Remote roles that are usable from Canada

Initial experience levels:

- Internship
- Entry-level
- 0-2 years
- Any role where the match score is strong

## Primary job-to-be-done

When I am trying to get interviews, I want one place that finds relevant jobs, prepares tailored application material, and tracks my applications, so I can apply consistently without wasting time across job sites.

## Success metric

The app is successful when the user can open the workbook/dashboard and see:

- fresh matching jobs
- apply links
- match score
- tailored resume bullets
- cover letter draft
- application status
- follow-up date

The next action should be obvious: open apply link, copy/download tailored documents, apply, mark status.

## MVP scope

### Must have

- Streamlit dashboard
- Excel export/control center
- Job search config
- Job ingestion from multiple sources
- Deduplication
- Match scoring
- Tailored resume bullets
- Cover letter draft
- Resume `.docx` generation per job
- Cover letter `.docx` generation per job
- Application tracker
- Follow-up date calculation
- Local storage only
- Optional AI provider selection per run

### Must not have in v1

- Cloud account/login
- Hosted database
- Auto-apply
- Browser automation that submits forms
- Storing private resume/profile data unencrypted
- Fragile LinkedIn-only scraping as the core system

## Source strategy

“Scrape any website” is not realistic as a first-class guarantee. Some sites aggressively block scraping. The durable design is adapter-based.

### Initial sources

1. LinkedIn
   - v1 fallback: search URL generator + manual import/paste support
   - later: browser-assisted extraction if legally and technically acceptable
2. Indeed
   - scrape/public HTML where possible
   - fallback: search URL generator
3. Google Jobs
   - v1 fallback: generated search links and parsed web results where possible
4. Company career pages
   - prioritize Greenhouse and Lever adapters
   - add Workday later
5. Canada Job Bank
   - scrape/public pages if accessible

### Adapter contract

Each source returns normalized jobs:

- source
- source_job_id
- title
- company
- location
- remote_type
- description
- apply_url
- posted_date
- scraped_at

## Excel workbook columns

- Date found
- Company
- Job title
- Location
- Remote/hybrid/onsite
- Source
- Apply link
- Match score
- Match reason
- Missing skills
- Keywords to add
- Tailored resume summary
- Tailored resume bullets
- Cover letter draft
- Resume file path
- Cover letter file path
- Status
- Applied date
- Follow-up date
- Notes

## Dashboard screens

### 1. Setup

- Upload/import base resume
- Enter target titles: data analyst variants
- Enter target locations: GTA, BC, Halifax
- Select sources
- Choose AI mode:
  - local-only
  - API provider
  - rules/templates only

### 2. Find jobs

- Run search
- Show source status
- Show jobs found
- Show duplicates removed
- Export/update Excel

### 3. Review jobs

- Filter by match score, location, source, status
- See job description
- See missing skills
- Open apply link

### 4. Tailor application

- Generate tailored resume bullets
- Generate cover letter draft
- Generate `.docx` files
- Save output path into Excel

### 5. Tracker

- Status board:
  - Found
  - Ready to apply
  - Applied
  - Follow-up due
  - Interview
  - Rejected
  - Offer
- Follow-up reminders inside dashboard/Excel

## Privacy/security requirements

- No cloud database.
- Store data locally by default.
- Keep `.env`, resumes, generated docs, local databases, and Excel files out of git.
- User can choose AI mode per run.
- If API AI is used, clearly warn that resume/job text leaves the machine.
- Store private profile/resume config encrypted if persisted beyond the session.
- Never commit secrets or personal resumes.

## Recommended architecture

```text
app.py
jobtool/
  config.py
  models.py
  sources/
    base.py
    indeed.py
    canada_job_bank.py
    greenhouse.py
    lever.py
    search_links.py
  matching.py
  tailoring.py
  documents.py
  workbook.py
  storage.py
  security.py
  tracker.py
tests/
  test_sources_*.py
  test_matching.py
  test_workbook.py
  test_tailoring.py
```

## Build phases

### Phase 1 — Product-correct local MVP

- Add job search config
- Add normalized job model
- Add workbook writer
- Add match scoring
- Add generated search links for LinkedIn, Indeed, Google Jobs
- Add manual job paste/import
- Preserve existing resume/cover-letter generation
- Improve tracker workflow

### Phase 2 — Real source adapters

- Canada Job Bank adapter
- Greenhouse adapter
- Lever adapter
- Indeed adapter if stable
- Deduplication across sources

### Phase 3 — Strong tailoring

- Better skill extraction
- Missing skills report
- Tailored resume summary
- Tailored bullet rewrites
- Cover letter per job
- `.docx` package generation

### Phase 4 — Privacy hardening

- Encrypted local profile storage
- Clear AI mode selection
- Secret-safe `.gitignore`
- Local-only mode documentation

### Phase 5 — Apply workflow

- One-click open apply links
- Status update buttons
- Follow-up reminder dates
- Daily “apply queue” view

## Non-goals

- Do not promise guaranteed interviews.
- Do not auto-apply in v1.
- Do not depend on LinkedIn scraping as the only job source.
- Do not make users configure complicated APIs before they can use the app.

## Current product decision

Rebuild the app around the workbook/dashboard workflow, not around a passive tracker. The app should produce an apply-ready queue every time it runs.
