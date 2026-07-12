from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from jobtool.documents import extract_resume_text
from jobtool.job_parser import fetch_job_text, parse_job
from jobtool.models import JobLead, SearchConfig
from jobtool.pipeline import prepare_application_package
from jobtool.security import EncryptedStore
from jobtool.sources.search_links import search_link_jobs
from jobtool.workbook import read_application_workbook, write_application_workbook

ROOT = Path(__file__).parent
OUTPUTS = ROOT / "outputs"
DATA = ROOT / "data"
TRACKER = ROOT / "applications.xlsx"
PROFILE = DATA / "profile.enc"
OUTPUTS.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)

st.set_page_config(page_title="Job Application Command Center", layout="wide")
st.title("Job Application Command Center")
st.caption("Find jobs → score fit → generate tailored resume + cover letter → track applications in Excel.")

DEFAULT_TITLES = [
    "data analyst",
    "junior data analyst",
    "entry level data analyst",
    "business intelligence analyst",
    "reporting analyst",
    "BI analyst",
]
DEFAULT_LOCATIONS = ["GTA", "Toronto ON", "British Columbia", "Vancouver BC", "Halifax NS", "Remote Canada"]
DEFAULT_SOURCES = ["linkedin", "indeed", "google_jobs", "canada_job_bank"]

with st.sidebar:
    st.header("Private profile")
    applicant_name = st.text_input("Name", value="Ashish Sachdev")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    location = st.text_input("Location", value="Canada")
    ai_mode = st.selectbox("AI mode", ["Rules/templates only", "Local-only AI later", "API AI later"], index=0)
    st.caption("v1 uses rules/templates only. API/local AI hooks are explicit so private data does not leave the machine by accident.")

    password = st.text_input("Encryption password", type="password", help="Used only if you save/load the local encrypted profile.")
    c1, c2 = st.columns(2)
    if c1.button("Save encrypted profile"):
        if not password:
            st.error("Enter an encryption password first.")
        else:
            EncryptedStore(PROFILE, password).save_json(
                {"name": applicant_name, "email": email, "phone": phone, "location": location}
            )
            st.success("Encrypted profile saved locally.")
    if c2.button("Load profile"):
        if not password:
            st.error("Enter the encryption password first.")
        elif not PROFILE.exists():
            st.error("No encrypted profile saved yet.")
        else:
            try:
                profile = EncryptedStore(PROFILE, password).load_json(password)
                st.session_state["loaded_profile"] = profile
                st.success("Profile decrypted. Copy values from below if needed.")
                st.json(profile)
            except ValueError as exc:
                st.error(str(exc))

st.warning("Privacy: generated docs, Excel files, resumes, and encrypted profiles stay local. Do not commit personal files to git.", icon="🔒")

tabs = st.tabs(["1. Find jobs", "2. Tailor package", "3. Tracker"])

with tabs[0]:
    st.subheader("Build the apply-ready job queue")
    st.caption("Enter any job searches you want. One query per line. Enter any locations you want. The app creates a queue for every query × location × source.")
    titles_text = st.text_area("Search queries / job titles", value="\n".join(DEFAULT_TITLES), height=140, placeholder="data analyst\nfinancial analyst\nhealthcare data analyst")
    locations_text = st.text_area("Locations", value="\n".join(DEFAULT_LOCATIONS), height=120, placeholder="Toronto ON\nCalgary AB\nRemote Canada\nNew York remote")
    source_labels = {
        "linkedin": "LinkedIn",
        "indeed": "Indeed",
        "google_jobs": "Google Jobs",
        "canada_job_bank": "Canada Job Bank",
    }
    selected_sources = st.multiselect(
        "Sources",
        options=list(source_labels.keys()),
        default=DEFAULT_SOURCES,
        format_func=lambda value: source_labels[value],
    )

    if st.button("Generate job queue in Excel", type="primary"):
        config = SearchConfig.from_text(
            queries_text=titles_text,
            locations_text=locations_text,
            sources=selected_sources,
        )
        if not config.search_queries:
            st.error("Add at least one search query/job title.")
            st.stop()
        if not config.locations:
            st.error("Add at least one location.")
            st.stop()
        if not config.sources:
            st.error("Select at least one source.")
            st.stop()
        jobs = search_link_jobs(config)
        write_application_workbook(TRACKER, jobs, append=True)
        st.success(f"Added/updated {len(jobs)} search queue rows in applications.xlsx.")
        st.dataframe(read_application_workbook(TRACKER), use_container_width=True)
        with open(TRACKER, "rb") as f:
            st.download_button("Download Excel command center", f, file_name="applications.xlsx")

with tabs[1]:
    st.subheader("Create tailored resume + cover letter")
    resume_file = st.file_uploader("Upload base resume", type=["docx", "pdf", "txt"])
    job_link = st.text_input("Apply/job posting link")
    job_text_manual = st.text_area(
        "Job posting text",
        height=260,
        placeholder="Paste the job description here. If the link can be read, this can be blank.",
    )
    company_override = st.text_input("Company override", placeholder="Optional")
    title_override = st.text_input("Job title override", placeholder="Optional")
    job_location = st.text_input("Job location", placeholder="Toronto, Vancouver, Halifax, Remote Canada...")

    if st.button("Generate tailored package", type="primary"):
        if ai_mode != "Rules/templates only":
            st.error("That AI mode is not implemented yet. Use rules/templates only for v1 privacy-safe generation.")
            st.stop()
        if not resume_file:
            st.error("Upload your resume first.")
            st.stop()
        if not job_link and not job_text_manual.strip():
            st.error("Paste a job link or job description.")
            st.stop()

        resume_text = extract_resume_text(resume_file)
        fetched_text = ""
        fetch_error = ""
        if job_link:
            try:
                fetched_text = fetch_job_text(job_link)
            except Exception as exc:  # noqa: BLE001 - show actionable fallback to user
                fetch_error = str(exc)
        job_text = job_text_manual.strip() or fetched_text.strip()
        if not job_text:
            st.error(f"Could not read the link. Paste the job description manually. Error: {fetch_error}")
            st.stop()

        parsed = parse_job(job_text, job_link)
        job = JobLead(
            title=title_override or parsed.title,
            company=company_override or parsed.company,
            location=job_location,
            source="Manual/link import",
            apply_url=job_link,
            description=job_text,
        )
        prepared = prepare_application_package(
            job=job,
            resume_text=resume_text,
            applicant_name=applicant_name,
            contact={"email": email, "phone": phone, "location": location},
            output_dir=OUTPUTS,
        )
        write_application_workbook(TRACKER, [prepared], append=True)

        st.success("Application package created and logged.")
        c1, c2, c3 = st.columns(3)
        c1.metric("Company", prepared.company or "Unknown")
        c2.metric("Role", prepared.title or "Unknown")
        c3.metric("Match score", f"{prepared.match_score}%")

        st.subheader("Missing skills / keywords to add honestly")
        st.write(", ".join(prepared.missing_keywords) or "None")
        st.subheader("Tailored resume bullets")
        st.write("\n".join(f"- {bullet}" for bullet in prepared.tailored_bullets))
        st.subheader("Cover letter draft")
        st.text_area("Cover letter", value=prepared.cover_letter, height=260)

        with open(prepared.resume_path, "rb") as f:
            st.download_button("Download tailored resume", f, file_name=Path(prepared.resume_path).name)
        with open(prepared.cover_letter_path, "rb") as f:
            st.download_button("Download cover letter", f, file_name=Path(prepared.cover_letter_path).name)
        with open(TRACKER, "rb") as f:
            st.download_button("Download updated Excel", f, file_name="applications.xlsx")

with tabs[2]:
    st.subheader("Application tracker")
    df = read_application_workbook(TRACKER)
    if df.empty:
        st.info("No applications yet. Generate a job queue or tailored package first.")
    else:
        status_filter = st.multiselect("Status filter", sorted(df["Status"].dropna().unique().tolist()))
        view = df[df["Status"].isin(status_filter)] if status_filter else df
        st.dataframe(view, use_container_width=True)
        csv = view.to_csv(index=False).encode("utf-8")
        st.download_button("Download tracker CSV", csv, file_name="applications.csv", mime="text/csv")
        with open(TRACKER, "rb") as f:
            st.download_button("Download tracker Excel", f, file_name="applications.xlsx")
