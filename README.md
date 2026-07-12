# Job Application Tool

A local job-application assistant for students and early-career applicants.

You upload your resume, paste a job posting or job link, and the app creates:

- a tailored resume `.docx`
- a tailored cover letter `.docx`
- an Excel tracker row with the job link and generated document paths

The tool runs locally on your device. No API key is required.

## Features

- Upload resume as `.docx`, `.pdf`, or `.txt`
- Paste a job link or full job description
- Extract important keywords from the job posting
- Compare the job posting against your resume
- Show matched and missing keywords
- Generate a tailored resume draft without inventing experience
- Generate a cover letter draft
- Save generated files in `outputs/`
- Track applications in `applications.xlsx`

## Important rule

This tool helps rewrite and reorganize your real experience. It does **not** fake skills, jobs, degrees, or projects.

If a keyword is missing, add it only if it is true and you can prove it with coursework, projects, internships, or portfolio work.

## Project structure

```text
job-application-tool/
├── app.py                       # Streamlit web app
├── pyproject.toml               # Python dependencies
├── README.md                    # Setup and usage guide
├── src/jobtool/
│   ├── documents.py             # Resume extraction and docx writing
│   ├── job_parser.py            # Job link/text parser
│   ├── tailor.py                # Keyword matching + document drafts
│   └── tracker.py               # Excel tracker writer
├── tests/                       # Automated tests
├── outputs/                     # Generated resumes and cover letters, created at runtime
└── applications.xlsx            # Excel tracker, created at runtime
```

## Requirements

- Python 3.11 or newer
- Internet connection for first install
- A browser
- Recommended: `uv`, the Python package manager

## Setup on any device

### Option A: Easiest setup with `uv`

#### Windows PowerShell

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
git clone <REPO_URL> job-application-tool
cd job-application-tool
uv sync
uv run streamlit run app.py
```

#### macOS or Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone <REPO_URL> job-application-tool
cd job-application-tool
uv sync
uv run streamlit run app.py
```

If `uv` installs successfully but the command is not found, close and reopen your terminal.

### Option B: Standard Python setup without `uv`

#### Windows PowerShell

```powershell
git clone <REPO_URL> job-application-tool
cd job-application-tool
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install streamlit pandas openpyxl python-docx pypdf requests beautifulsoup4 pytest
streamlit run app.py
```

#### macOS or Linux

```bash
git clone <REPO_URL> job-application-tool
cd job-application-tool
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install streamlit pandas openpyxl python-docx pypdf requests beautifulsoup4 pytest
streamlit run app.py
```

## If you do not have Git

Download the repo as a ZIP, unzip it, open a terminal in the folder, then run either the `uv` or standard Python setup above starting from the `cd job-application-tool` step.

## How to use

1. Start the app:

```bash
uv run streamlit run app.py
```

2. Open the local URL printed by Streamlit, usually:

```text
http://localhost:8501
```

3. Fill your details in the sidebar:
   - name
   - email
   - phone
   - location

4. Upload your resume.

5. Paste either:
   - the job posting link, or
   - the full job description text

6. Click **Generate application package**.

7. Download:
   - tailored resume
   - cover letter
   - Excel tracker

## Where files are saved

Generated documents:

```text
outputs/
```

Application tracker:

```text
applications.xlsx
```

Each Excel row includes:

- timestamp
- company
- role
- job link
- match score
- matched keywords
- missing keywords
- tailored resume path
- cover letter path
- application status

## Testing

Run this before sharing changes:

```bash
uv run pytest -q
```

Expected result:

```text
3 passed
```

## Common problems

### Streamlit command not found

Use:

```bash
uv run streamlit run app.py
```

or activate your virtual environment first.

### Job link does not load

Some job boards block automated scraping. This is normal.

Fix: copy and paste the full job description into the text box.

### PDF resume text looks broken

Some PDFs are image scans or badly exported.

Fix: upload a `.docx` version of your resume if possible.

### Excel file is open and app cannot save

Close `applications.xlsx`, then generate again.

## Privacy

Everything runs locally. The app does not upload your resume to an external API.

The only network request happens when you paste a job link and the app tries to read that page.

## Development notes

Do not commit personal generated files:

- `outputs/`
- `applications.xlsx`
- `.venv/`

They are ignored by `.gitignore`.

## Roadmap

Possible upgrades:

- better job title/company extraction
- one-click LinkedIn/Indeed import
- status pipeline: saved, applied, interview, rejected, offer
- dashboard showing applications by week
- optional LLM rewriting with strict no-fabrication rules
