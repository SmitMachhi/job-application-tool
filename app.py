from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from jobtool.documents import extract_resume_text, save_docx
from jobtool.job_parser import fetch_job_text, parse_job
from jobtool.tailor import build_cover_letter, build_tailored_resume, extract_keywords, score_match
from jobtool.tracker import append_application

ROOT = Path(__file__).parent
OUTPUTS = ROOT / "outputs"
TRACKER = ROOT / "applications.xlsx"
OUTPUTS.mkdir(exist_ok=True)

st.set_page_config(page_title="Job Application Tool", layout="wide")
st.title("Job Application Tool")
st.caption("Upload resume → paste job → generate tailored resume + cover letter → log to Excel.")

with st.sidebar:
    st.header("Your details")
    applicant_name = st.text_input("Name", value="Ashish Sachdev")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    location = st.text_input("Location", value="Vadodara, India")

resume_file = st.file_uploader("Upload resume", type=["docx", "pdf", "txt"])
job_link = st.text_input("Job posting link")
job_text_manual = st.text_area("Job posting text", height=260, placeholder="Paste full job description here. If link scraping works, this can be blank.")

if st.button("Generate application package", type="primary"):
    if not resume_file:
        st.error("Upload your resume first.")
        st.stop()
    if not job_link and not job_text_manual.strip():
        st.error("Paste a job link or the job posting text.")
        st.stop()

    resume_text = extract_resume_text(resume_file)
    fetched_text = ""
    fetch_error = ""
    if job_link:
        try:
            fetched_text = fetch_job_text(job_link)
        except Exception as exc:
            fetch_error = str(exc)

    job_text = job_text_manual.strip() or fetched_text.strip()
    if not job_text:
        st.error(f"Could not read the job link. Paste the job description manually. Error: {fetch_error}")
        st.stop()

    job = parse_job(job_text, job_link)
    keywords = extract_keywords(job_text)
    matched, missing, match_score = score_match(resume_text, keywords)

    safe_company = re.sub(r"[^A-Za-z0-9]+", "_", job.company or "Company").strip("_")
    safe_role = re.sub(r"[^A-Za-z0-9]+", "_", job.title or "Role").strip("_")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = f"{stamp}_{safe_company}_{safe_role}"

    tailored_resume = build_tailored_resume(
        applicant_name=applicant_name,
        contact={"email": email, "phone": phone, "location": location},
        original_resume=resume_text,
        job=job,
        matched_keywords=matched,
        missing_keywords=missing,
    )
    cover_letter = build_cover_letter(
        applicant_name=applicant_name,
        contact={"email": email, "phone": phone, "location": location},
        resume_text=resume_text,
        job=job,
        matched_keywords=matched,
    )

    resume_path = OUTPUTS / f"{prefix}_tailored_resume.docx"
    cover_path = OUTPUTS / f"{prefix}_cover_letter.docx"
    save_docx(tailored_resume, resume_path)
    save_docx(cover_letter, cover_path)

    append_application(
        TRACKER,
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "company": job.company,
            "role": job.title,
            "job_link": job_link,
            "match_score": match_score,
            "matched_keywords": ", ".join(matched[:25]),
            "missing_keywords": ", ".join(missing[:25]),
            "resume_path": str(resume_path),
            "cover_letter_path": str(cover_path),
            "status": "Drafted",
        },
    )

    st.success("Done. Application package created and logged.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Company", job.company or "Unknown")
    c2.metric("Role", job.title or "Unknown")
    c3.metric("Match score", f"{match_score}%")

    st.subheader("Matched keywords")
    st.write(", ".join(matched[:50]) or "None found")
    st.subheader("Missing keywords to honestly improve")
    st.write(", ".join(missing[:50]) or "None")

    with open(resume_path, "rb") as f:
        st.download_button("Download tailored resume", f, file_name=resume_path.name)
    with open(cover_path, "rb") as f:
        st.download_button("Download cover letter", f, file_name=cover_path.name)
    with open(TRACKER, "rb") as f:
        st.download_button("Download Excel tracker", f, file_name="applications.xlsx")

if TRACKER.exists():
    st.divider()
    st.subheader("Application tracker")
    st.dataframe(pd.read_excel(TRACKER), use_container_width=True)
