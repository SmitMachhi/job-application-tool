# Career Path + Job Application Command Center

A local-first PathPilot-style career navigation and job application command center.

It helps you map realistic career paths, identify skill gaps, create a project roadmap, generate job-search queues, and then tailor resume/cover-letter files for real postings. It deliberately does **not** include AI interview practice or interview simulation features.

## What it does now

- Builds a PathPilot-style career plan:
  - target role recommendations
  - fit score by role
  - matched skills
  - missing skills
  - 4-week execution roadmap
  - downloadable `career_path.xlsx`
- Creates a job-search config from the career plan
- Creates an apply-ready Excel workbook: `applications.xlsx`
- Lets you search any job query in any location
- Generates search queues for 16 sources:
  - LinkedIn
  - Indeed
  - Google Jobs
  - Canada Job Bank
  - Glassdoor
  - ZipRecruiter
  - Workopolis
  - Monster
  - Wellfound
  - Built In
  - SimplyHired
  - Eluta
  - Talent.com
  - Careerjet
  - Greenhouse company pages
  - Lever company pages
- Targets data analyst-style roles across:
  - GTA
  - British Columbia
  - Halifax
  - Remote Canada
- Lets you paste a job description or job link
- Scores resume/job match
- Shows missing skills/keywords honestly
- Generates:
  - tailored resume `.docx`
  - cover letter `.docx`
- Tracks status and follow-up dates
- Saves generated files in `outputs/`
- Supports encrypted local profile storage in `data/profile.enc`

## What it does not do yet

- It does not include AI interview practice, mock interviews, interview simulation, or interview coaching.
- It does not auto-apply.
- It does not bypass LinkedIn/Indeed scraping protections.
- It does not upload your resume to AI by default.
- It does not promise interviews.

The current AI mode lets you select:

- **Rules/templates only**: active now, fully local
- **Local AI**: selectable, falls back to rules/templates until a local model is configured
- **API AI**: selectable, falls back to rules/templates until an API provider is configured

## Privacy

Everything runs locally.

Private/runtime files are gitignored:

- `outputs/`
- `data/`
- `applications.xlsx`
- `.env`
- local databases
- virtualenv/cache files

If you save a profile, it is encrypted with your password using `cryptography`/Fernet. Lose the password and the app cannot recover it.

## Setup with uv

### Windows PowerShell

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
git clone https://github.com/SmitMachhi/job-application-tool.git job-application-tool
cd job-application-tool
uv sync
uv run streamlit run app.py
```

### macOS/Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/SmitMachhi/job-application-tool.git job-application-tool
cd job-application-tool
uv sync
uv run streamlit run app.py
```

## Setup without uv

### Windows PowerShell

```powershell
git clone https://github.com/SmitMachhi/job-application-tool.git job-application-tool
cd job-application-tool
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[test]"
streamlit run app.py
```

### macOS/Linux

```bash
git clone https://github.com/SmitMachhi/job-application-tool.git job-application-tool
cd job-application-tool
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[test]"
streamlit run app.py
```

## How to use

### 1. Career path

Open the app and go to **Career path**.

- Add current starting point
- Add target roles, one per line
- Add current skills/tools
- Add interests, industries, and constraints
- Add search locations
- Click **Generate career path**

The app shows role recommendations, fit scores, missing skills, a four-week roadmap, and a downloadable career plan Excel file. The generated roles/locations can seed the **Find jobs** tab.

### 2. Find jobs

Open the app and go to **Find jobs**.

- Enter any search queries/job titles, one per line
- Enter any locations, one per line
- Pick sources
- Click **Generate job queue in Excel**

The app creates rows for every query × location × source combination. Example:

```text
Search queries:
data analyst
financial analyst
healthcare data analyst

Locations:
Toronto ON
Calgary AB
Remote Canada
New York remote
```

This updates `applications.xlsx` and the dashboard tracker with source links you can open immediately.

Options:

- Leave **Replace existing Excel/tracker list** off to append/dedupe new searches.
- Turn it on to rebuild the tracker from only the current search.
- In **Tracker**, filter rows and download either filtered CSV, filtered Excel, or full Excel.
- The **Apply link** column is clickable in the dashboard, so you can open the job site directly.

### 3. Tailor package

Go to **Tailor package**.

- Upload your base resume
- Paste a job link and/or full job description
- Add company/title override if parsing is weak
- Click **Generate tailored package**

The app creates:

- tailored resume `.docx`
- cover letter `.docx`
- updated Excel tracker row

### 4. Tracker

Go to **Tracker**.

Use the table to review jobs, statuses, follow-up dates, and file paths.

## Excel columns

The workbook includes:

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

## Testing

```bash
uv run pytest -q
```

Expected result:

```text
15 passed
```

## Current architecture

```text
app.py
jobtool/
  models.py
  career_path.py
  pipeline.py
  security.py
  workbook.py
  documents.py
  job_parser.py
  tailor.py
  tracker.py
  sources/
    search_links.py
tests/
  test_command_center.py
  test_tailor.py
  test_tracker.py
```

## Next build targets

1. Canada Job Bank real adapter
2. Greenhouse company-career adapter
3. Lever company-career adapter
4. Better dedupe across real postings
5. Local/API AI rewriting with explicit consent per run
6. One-click open/apply queue workflow
