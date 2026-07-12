from __future__ import annotations

from pathlib import Path

import pandas as pd

from jobtool.models import JobLead, SearchConfig
from jobtool.sources.search_links import build_search_links, search_link_jobs
from jobtool.workbook import APPLICATION_COLUMNS, write_application_workbook
from jobtool.security import EncryptedStore
from jobtool.pipeline import prepare_application_package


def test_search_links_cover_selected_sources_and_locations():
    config = SearchConfig(
        target_titles=["data analyst"],
        locations=["GTA", "BC", "Halifax"],
        sources=["linkedin", "indeed", "google_jobs", "canada_job_bank"],
    )

    links = build_search_links(config)

    assert {link.source for link in links} == {"LinkedIn", "Indeed", "Google Jobs", "Canada Job Bank"}
    assert any("data+analyst" in link.url for link in links)
    assert any("Halifax" in link.query for link in links)


def test_search_link_jobs_create_apply_ready_fallback_rows():
    config = SearchConfig.default_data_analyst()

    jobs = search_link_jobs(config)

    assert jobs
    assert all(job.apply_url.startswith("https://") for job in jobs)
    assert all(job.source in {"LinkedIn", "Indeed", "Google Jobs", "Canada Job Bank"} for job in jobs)
    role_terms = ["data analyst", "bi analyst", "reporting analyst", "business intelligence analyst"]
    assert all(any(term in job.title.lower() for term in role_terms) for job in jobs)


def test_write_application_workbook_uses_command_center_columns(tmp_path: Path):
    job = JobLead(
        title="Junior Data Analyst",
        company="Example Co",
        location="Toronto, ON",
        source="Canada Job Bank",
        apply_url="https://example.com/apply",
        description="SQL Excel dashboards",
        match_score=80,
        matched_keywords=["sql", "excel"],
        missing_keywords=["tableau"],
        tailored_summary="Data analyst summary",
        tailored_bullets=["Built Excel dashboards"],
        cover_letter="Dear Hiring Manager",
        resume_path="outputs/resume.docx",
        cover_letter_path="outputs/cover.docx",
    )
    workbook = tmp_path / "applications.xlsx"

    write_application_workbook(workbook, [job])

    df = pd.read_excel(workbook)
    assert list(df.columns) == APPLICATION_COLUMNS
    assert df.loc[0, "Company"] == "Example Co"
    assert df.loc[0, "Status"] == "Ready to apply"
    assert df.loc[0, "Follow-up date"]


def test_encrypted_store_round_trips_without_plaintext(tmp_path: Path):
    store_path = tmp_path / "profile.enc"
    store = EncryptedStore(store_path, password="strong password")

    store.save_json({"resume": "private resume text", "email": "person@example.com"})

    raw = store_path.read_bytes()
    assert b"private resume text" not in raw
    assert b"person@example.com" not in raw
    assert store.load_json(password="strong password") == {"resume": "private resume text", "email": "person@example.com"}


def test_prepare_application_package_generates_docs_and_job_row(tmp_path: Path):
    job = JobLead(
        title="Entry Level Data Analyst",
        company="Acme Analytics",
        location="Vancouver, BC",
        source="Manual",
        apply_url="https://example.com/job",
        description="Looking for SQL, Excel, Power BI, reporting, dashboards, communication.",
    )
    resume_text = "Ashish Sachdev\nSQL Excel reporting dashboard project communication"

    prepared = prepare_application_package(
        job=job,
        resume_text=resume_text,
        applicant_name="Ashish Sachdev",
        contact={"email": "ashish@example.com", "location": "Canada"},
        output_dir=tmp_path,
    )

    assert prepared.match_score > 0
    assert "SQL" in prepared.tailored_summary or "sql" in prepared.tailored_summary.lower()
    assert Path(prepared.resume_path).exists()
    assert Path(prepared.cover_letter_path).exists()
