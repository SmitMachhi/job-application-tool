from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from jobtool.models import JobLead

APPLICATION_COLUMNS = [
    "Date found",
    "Company",
    "Job title",
    "Location",
    "Remote/hybrid/onsite",
    "Source",
    "Apply link",
    "Match score",
    "Match reason",
    "Missing skills",
    "Keywords to add",
    "Tailored resume summary",
    "Tailored resume bullets",
    "Cover letter draft",
    "Resume file path",
    "Cover letter file path",
    "Status",
    "Applied date",
    "Follow-up date",
    "Notes",
]


def job_to_row(job: JobLead) -> dict[str, str | int]:
    follow_up = job.follow_up_date or (datetime.now() + timedelta(days=7)).date().isoformat()
    return {
        "Date found": job.scraped_at.split("T")[0],
        "Company": job.company,
        "Job title": job.title,
        "Location": job.location,
        "Remote/hybrid/onsite": job.remote_type,
        "Source": job.source,
        "Apply link": job.apply_url,
        "Match score": job.match_score,
        "Match reason": job.match_reason,
        "Missing skills": ", ".join(job.missing_keywords),
        "Keywords to add": ", ".join(job.keywords_to_add),
        "Tailored resume summary": job.tailored_summary,
        "Tailored resume bullets": "\n".join(job.tailored_bullets),
        "Cover letter draft": job.cover_letter,
        "Resume file path": job.resume_path,
        "Cover letter file path": job.cover_letter_path,
        "Status": job.status or "Ready to apply",
        "Applied date": job.applied_date,
        "Follow-up date": follow_up,
        "Notes": job.notes,
    }


def write_application_workbook(path: Path, jobs: list[JobLead], append: bool = False) -> None:
    rows = [job_to_row(job) for job in jobs]
    df = pd.DataFrame(rows, columns=APPLICATION_COLUMNS)
    if append and path.exists():
        existing = pd.read_excel(path)
        for column in APPLICATION_COLUMNS:
            if column not in existing.columns:
                existing[column] = ""
        df = pd.concat([existing[APPLICATION_COLUMNS], df], ignore_index=True)
        df = df.drop_duplicates(subset=["Company", "Job title", "Location", "Apply link"], keep="first")
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(path, index=False)


def read_application_workbook(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=APPLICATION_COLUMNS)
    df = pd.read_excel(path)
    for column in APPLICATION_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df[APPLICATION_COLUMNS]
