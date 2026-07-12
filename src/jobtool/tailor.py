from __future__ import annotations

import re
from collections import Counter
from typing import Iterable

from jobtool.job_parser import JobPosting

STOPWORDS = {
    "and", "the", "for", "with", "you", "your", "our", "are", "from", "that", "this", "will", "have", "has", "job",
    "role", "team", "work", "company", "experience", "candidate", "skills", "ability", "responsibilities", "requirements",
    "about", "into", "using", "use", "can", "all", "their", "they", "who", "what", "when", "where", "how", "why",
}
IMPORTANT_TERMS = {
    "python", "sql", "excel", "power bi", "tableau", "dashboard", "analytics", "data analysis", "data analyst",
    "machine learning", "statistics", "reporting", "etl", "database", "pandas", "numpy", "visualization", "business intelligence",
    "communication", "stakeholder", "problem solving", "automation", "git", "api", "aws", "azure", "gcp",
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def extract_keywords(job_text: str, limit: int = 45) -> list[str]:
    text = normalize(job_text)
    phrases = [term for term in IMPORTANT_TERMS if term in text]
    words = re.findall(r"[a-z][a-z0-9+#.]{2,}", text)
    counts = Counter(w for w in words if w not in STOPWORDS and not w.isdigit())
    common = [w for w, _ in counts.most_common(limit) if len(w) > 2]
    result = []
    for item in phrases + common:
        if item not in result:
            result.append(item)
    return result[:limit]


def score_match(resume_text: str, keywords: Iterable[str]) -> tuple[list[str], list[str], int]:
    resume = normalize(resume_text)
    matched, missing = [], []
    for keyword in keywords:
        if normalize(keyword) in resume:
            matched.append(keyword)
        else:
            missing.append(keyword)
    score = round((len(matched) / max(1, len(matched) + len(missing))) * 100)
    return matched, missing, score


def build_tailored_resume(applicant_name: str, contact: dict[str, str], original_resume: str, job: JobPosting, matched_keywords: list[str], missing_keywords: list[str]) -> str:
    contact_line = " | ".join(v for v in [contact.get("email"), contact.get("phone"), contact.get("location")] if v)
    matched_line = ", ".join(matched_keywords[:18]) or "relevant technical and communication skills"
    missing_line = ", ".join(missing_keywords[:10]) or "None"
    return f"""# {applicant_name}
{contact_line}

## Target Role
{job.title} at {job.company}

## Professional Summary
Entry-level data/technology candidate aligned to this role through demonstrated fit in: {matched_line}. Focused on clear analysis, accurate reporting, structured problem solving, and learning quickly in practical business environments.

## Core Skills Matched to Posting
{bullet_list(matched_keywords[:24])}

## Resume Content To Keep and Reorder
The original resume content below is preserved so experience is not invented. Reorder bullets to put the most relevant projects, tools, coursework, internships, and achievements first.

{original_resume.strip()}

## Gaps To Address Honestly
Do not fake these. If true, add proof through projects, coursework, or portfolio links: {missing_line}.
"""


def build_cover_letter(applicant_name: str, contact: dict[str, str], resume_text: str, job: JobPosting, matched_keywords: list[str]) -> str:
    contact_line = " | ".join(v for v in [contact.get("email"), contact.get("phone"), contact.get("location")] if v)
    skills = ", ".join(matched_keywords[:8]) or "data analysis, problem solving, and communication"
    return f"""# Cover Letter
{applicant_name}
{contact_line}

Dear Hiring Manager,

I am applying for the {job.title} role at {job.company}. My background matches the posting most strongly in {skills}. I am interested in this role because it requires practical execution, attention to detail, and the ability to turn information into useful decisions.

From my resume, the most relevant strengths are my technical foundation, willingness to learn quickly, and ability to communicate work clearly. I would bring a reliable, detail-oriented approach to the team and keep improving through direct feedback and measurable output.

I would appreciate the opportunity to discuss how I can contribute to {job.company} in this role.

Sincerely,
{applicant_name}
"""


def bullet_list(items: list[str]) -> str:
    if not items:
        return "- Add role-relevant skills here after verifying they are true."
    return "\n".join(f"- {item}" for item in items)
