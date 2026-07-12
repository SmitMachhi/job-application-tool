from __future__ import annotations

from pathlib import Path

import pandas as pd

from jobtool.ai_modes import AI_MODES, resolve_ai_mode
from jobtool.career_path import CareerProfile, build_career_plan, career_plan_to_dataframe, recommend_roles
from jobtool.models import JobLead, SearchConfig
from jobtool.sources.search_links import SOURCE_LABELS, build_search_links, search_link_jobs
from jobtool.workbook import APPLICATION_COLUMNS, dataframe_to_excel_bytes, write_application_workbook
from jobtool.security import EncryptedStore
from jobtool.pipeline import prepare_application_package


def test_career_profile_dedupes_skills_and_goals():
    profile = CareerProfile.from_text(
        current_role="student",
        target_roles_text="Data Analyst\nBI Analyst\nData Analyst",
        skills_text="SQL\nExcel\nsql\nPower BI",
        interests_text="healthcare\nfinance",
        constraints_text="Canada only\nremote preferred",
    )

    assert profile.target_roles == ["Data Analyst", "BI Analyst"]
    assert profile.skills == ["SQL", "Excel", "Power BI"]
    assert profile.interests == ["healthcare", "finance"]
    assert profile.constraints == ["Canada only", "remote preferred"]


def test_recommend_roles_scores_fit_and_missing_skills_without_interview_features():
    profile = CareerProfile.from_text(
        current_role="BSc IT student",
        target_roles_text="Data Analyst\nBusiness Intelligence Analyst\nMachine Learning Engineer",
        skills_text="SQL\nExcel\nPython\ncommunication",
        interests_text="dashboards\nbusiness reporting",
        constraints_text="entry level\nCanada",
    )

    recommendations = recommend_roles(profile)

    assert recommendations[0].role == "Data Analyst"
    assert recommendations[0].fit_score >= recommendations[-1].fit_score
    assert "Power BI" in recommendations[0].missing_skills or "Tableau" in recommendations[0].missing_skills
    combined = " ".join(step.action for rec in recommendations for step in rec.roadmap)
    assert "interview" not in combined.lower()


def test_build_career_plan_creates_search_config_and_downloadable_rows():
    profile = CareerProfile.from_text(
        current_role="student",
        target_roles_text="Data Analyst\nBI Analyst",
        skills_text="SQL\nExcel",
        interests_text="analytics",
        constraints_text="Toronto\nRemote Canada",
    )

    plan = build_career_plan(profile, locations=["Toronto ON", "Remote Canada"])
    df = career_plan_to_dataframe(plan.recommendations)

    assert plan.search_config.target_titles[:2] == ["Data Analyst", "BI Analyst"]
    assert plan.search_config.locations == ["Toronto ON", "Remote Canada"]
    assert list(df.columns) == ["Role", "Fit score", "Why it fits", "Missing skills", "Next actions"]
    assert "interview" not in df.to_string().lower()


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


def test_search_config_accepts_custom_queries_and_any_location():
    config = SearchConfig.from_text(
        queries_text="financial analyst\nhealthcare data analyst\n",
        locations_text="Calgary AB\nNew York remote\n",
        sources=["linkedin", "google_jobs"],
    )

    links = build_search_links(config)
    jobs = search_link_jobs(config)

    assert config.target_titles == ["financial analyst", "healthcare data analyst"]
    assert config.locations == ["Calgary AB", "New York remote"]
    assert any("financial+analyst" in link.url and "Calgary+AB" in link.url for link in links)
    assert any("healthcare data analyst New York remote" == link.query for link in links)
    assert any(job.title == "Financial Analyst search queue" and job.location == "Calgary AB" for job in jobs)
    assert any(job.title == "Healthcare Data Analyst search queue" and job.location == "New York remote" for job in jobs)


def test_maximum_source_catalog_is_available():
    expected = {
        "linkedin",
        "indeed",
        "google_jobs",
        "canada_job_bank",
        "glassdoor",
        "ziprecruiter",
        "workopolis",
        "monster",
        "wellfound",
        "builtin",
        "simplyhired",
        "eluta",
        "talent_com",
        "careerjet",
        "greenhouse_google",
        "lever_google",
    }

    assert expected.issubset(SOURCE_LABELS)


def test_all_ai_modes_are_selectable_with_safe_fallback():
    assert {mode.key for mode in AI_MODES} == {"rules", "local", "api"}
    assert resolve_ai_mode("rules").enabled is True
    assert resolve_ai_mode("local").enabled is False
    assert "falls back" in resolve_ai_mode("api").message.lower()


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


def test_filtered_tracker_can_be_downloaded_as_excel_bytes():
    df = pd.DataFrame(
        [
            {"Company": "Ready Co", "Status": "Ready to apply", "Apply link": "https://example.com/ready"},
            {"Company": "Applied Co", "Status": "Applied", "Apply link": "https://example.com/applied"},
        ]
    )
    filtered = df[df["Status"] == "Ready to apply"]

    payload = dataframe_to_excel_bytes(filtered)
    reread = pd.read_excel(payload)

    assert reread["Company"].tolist() == ["Ready Co"]


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
