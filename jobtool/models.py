from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


def _clean_lines(text: str) -> list[str]:
    seen: set[str] = set()
    cleaned: list[str] = []
    for raw in text.splitlines():
        item = " ".join(raw.strip().split())
        key = item.lower()
        if item and key not in seen:
            seen.add(key)
            cleaned.append(item)
    return cleaned


@dataclass
class SearchConfig:
    target_titles: list[str]
    locations: list[str]
    sources: list[str]
    experience_levels: list[str] = field(default_factory=lambda: ["internship", "entry-level", "0-2 years", "any strong match"])

    @classmethod
    def from_text(cls, queries_text: str, locations_text: str, sources: list[str]) -> "SearchConfig":
        return cls(
            target_titles=_clean_lines(queries_text),
            locations=_clean_lines(locations_text),
            sources=sources,
        )

    @property
    def search_queries(self) -> list[str]:
        return self.target_titles

    @classmethod
    def default_data_analyst(cls) -> "SearchConfig":
        return cls(
            target_titles=[
                "data analyst",
                "junior data analyst",
                "entry level data analyst",
                "business intelligence analyst",
                "reporting analyst",
                "BI analyst",
            ],
            locations=["GTA", "Toronto ON", "British Columbia", "Vancouver BC", "Halifax NS", "Remote Canada"],
            sources=["linkedin", "indeed", "google_jobs", "canada_job_bank"],
        )


@dataclass
class SearchLink:
    source: str
    query: str
    url: str
    title: str = ""
    location: str = ""


@dataclass
class JobLead:
    title: str
    company: str
    location: str
    source: str
    apply_url: str
    description: str = ""
    source_job_id: str = ""
    remote_type: str = ""
    posted_date: str = ""
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    match_score: int = 0
    match_reason: str = ""
    matched_keywords: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)
    keywords_to_add: list[str] = field(default_factory=list)
    tailored_summary: str = ""
    tailored_bullets: list[str] = field(default_factory=list)
    cover_letter: str = ""
    resume_path: str = ""
    cover_letter_path: str = ""
    status: str = "Ready to apply"
    applied_date: str = ""
    follow_up_date: str = ""
    notes: str = ""
