from __future__ import annotations

import re
from pathlib import Path

from jobtool.documents import save_docx
from jobtool.models import JobLead
from jobtool.tailor import build_cover_letter, build_tailored_resume, extract_keywords, score_match
from jobtool.job_parser import JobPosting


def safe_slug(value: str, fallback: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", value or fallback).strip("_")
    return slug[:80] or fallback


def prepare_application_package(
    job: JobLead,
    resume_text: str,
    applicant_name: str,
    contact: dict[str, str],
    output_dir: Path,
) -> JobLead:
    keywords = extract_keywords(job.description or " ".join([job.title, job.company]))
    matched, missing, match_score = score_match(resume_text, keywords)
    posting = JobPosting(title=job.title, company=job.company, text=job.description, link=job.apply_url)

    tailored_resume = build_tailored_resume(
        applicant_name=applicant_name,
        contact=contact,
        original_resume=resume_text,
        job=posting,
        matched_keywords=matched,
        missing_keywords=missing,
    )
    cover_letter = build_cover_letter(
        applicant_name=applicant_name,
        contact=contact,
        resume_text=resume_text,
        job=posting,
        matched_keywords=matched,
    )

    prefix = f"{safe_slug(job.company, 'Company')}_{safe_slug(job.title, 'Role')}"
    resume_path = output_dir / f"{prefix}_tailored_resume.docx"
    cover_path = output_dir / f"{prefix}_cover_letter.docx"
    save_docx(tailored_resume, resume_path)
    save_docx(cover_letter, cover_path)

    job.match_score = match_score
    job.match_reason = f"Matched {len(matched)} of {len(matched) + len(missing)} extracted keywords."
    job.matched_keywords = matched
    job.missing_keywords = missing[:15]
    job.keywords_to_add = missing[:10]
    job.tailored_summary = _summary_from_resume(tailored_resume)
    job.tailored_bullets = [f"Emphasize verified experience with {kw}." for kw in matched[:8]] or [
        "Emphasize relevant coursework, projects, and measurable analysis work."
    ]
    job.cover_letter = cover_letter
    job.resume_path = str(resume_path)
    job.cover_letter_path = str(cover_path)
    job.status = "Ready to apply"
    return job


def _summary_from_resume(text: str) -> str:
    marker = "## Professional Summary"
    if marker not in text:
        return ""
    rest = text.split(marker, 1)[1].strip()
    return rest.split("\n\n", 1)[0].strip()
