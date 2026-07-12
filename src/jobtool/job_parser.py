from __future__ import annotations

import re
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass
class JobPosting:
    title: str
    company: str
    text: str
    link: str = ""


def fetch_job_text(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 job-application-tool/0.1"}
    res = requests.get(url, headers=headers, timeout=20)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = "\n".join(line.strip() for line in soup.get_text("\n").splitlines() if line.strip())
    if len(text) < 200:
        raise ValueError("Job page text too short; paste description manually")
    return text[:30000]


def parse_job(text: str, link: str = "") -> JobPosting:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    title = ""
    company = ""

    title_patterns = [
        r"(?:job title|position|role)\s*[:\-]\s*(.+)",
        r"hiring\s+(.+)",
    ]
    company_patterns = [
        r"(?:company|organization|employer)\s*[:\-]\s*(.+)",
        r"at\s+([A-Z][A-Za-z0-9&.,\- ]{2,60})",
    ]

    sample = "\n".join(lines[:30])
    for pat in title_patterns:
        m = re.search(pat, sample, flags=re.I)
        if m:
            title = clean_field(m.group(1))
            break
    for pat in company_patterns:
        m = re.search(pat, sample, flags=re.I)
        if m:
            company = clean_field(m.group(1))
            break

    if not title and lines:
        title = clean_field(lines[0])[:90]
    if not company:
        company = "Unknown Company"

    return JobPosting(title=title, company=company, text=text, link=link)


def clean_field(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip(" -|•\t")
    return value[:120]
