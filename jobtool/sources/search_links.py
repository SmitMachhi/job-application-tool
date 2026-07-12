from __future__ import annotations

from urllib.parse import quote_plus

from jobtool.models import JobLead, SearchConfig, SearchLink

SOURCE_LABELS = {
    "linkedin": "LinkedIn",
    "indeed": "Indeed",
    "google_jobs": "Google Jobs",
    "canada_job_bank": "Canada Job Bank",
    "glassdoor": "Glassdoor",
    "ziprecruiter": "ZipRecruiter",
    "workopolis": "Workopolis",
    "monster": "Monster",
    "wellfound": "Wellfound",
    "builtin": "Built In",
    "simplyhired": "SimplyHired",
    "eluta": "Eluta",
    "talent_com": "Talent.com",
    "careerjet": "Careerjet",
    "greenhouse_google": "Greenhouse company pages",
    "lever_google": "Lever company pages",
}

DEFAULT_SOURCE_KEYS = list(SOURCE_LABELS.keys())


def build_search_links(config: SearchConfig) -> list[SearchLink]:
    links: list[SearchLink] = []
    for title in config.target_titles:
        for location in config.locations:
            query = f"{title} {location}"
            encoded_query = quote_plus(query)
            encoded_title = quote_plus(title)
            encoded_location = quote_plus(location)
            for source in config.sources:
                label = SOURCE_LABELS.get(source, source.replace("_", " ").title())
                url = build_source_url(source, encoded_query, encoded_title, encoded_location)
                links.append(SearchLink(source=label, query=query, url=url, title=title, location=location))
    return links


def build_source_url(source: str, encoded_query: str, encoded_title: str, encoded_location: str) -> str:
    if source == "linkedin":
        return f"https://www.linkedin.com/jobs/search/?keywords={encoded_title}&location={encoded_location}"
    if source == "indeed":
        return f"https://ca.indeed.com/jobs?q={encoded_title}&l={encoded_location}"
    if source == "google_jobs":
        return f"https://www.google.com/search?q={encoded_query}+jobs"
    if source == "canada_job_bank":
        return f"https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring={encoded_title}&locationstring={encoded_location}"
    if source == "glassdoor":
        return f"https://www.glassdoor.ca/Job/jobs.htm?sc.keyword={encoded_title}&locT=C&locKeyword={encoded_location}"
    if source == "ziprecruiter":
        return f"https://www.ziprecruiter.com/jobs-search?search={encoded_title}&location={encoded_location}"
    if source == "workopolis":
        return f"https://www.workopolis.com/jobsearch/{encoded_title}-jobs/{encoded_location}"
    if source == "monster":
        return f"https://www.monster.ca/jobs/search?q={encoded_title}&where={encoded_location}"
    if source == "wellfound":
        return f"https://wellfound.com/jobs?query={encoded_title}&location={encoded_location}"
    if source == "builtin":
        return f"https://builtin.com/jobs?search={encoded_title}&location={encoded_location}"
    if source == "simplyhired":
        return f"https://www.simplyhired.ca/search?q={encoded_title}&l={encoded_location}"
    if source == "eluta":
        return f"https://www.eluta.ca/search?q={encoded_title}&l={encoded_location}"
    if source == "talent_com":
        return f"https://ca.talent.com/jobs?k={encoded_title}&l={encoded_location}"
    if source == "careerjet":
        return f"https://www.careerjet.ca/search/jobs?s={encoded_title}&l={encoded_location}"
    if source == "greenhouse_google":
        return f"https://www.google.com/search?q=site%3Aboards.greenhouse.io+{encoded_query}"
    if source == "lever_google":
        return f"https://www.google.com/search?q=site%3Ajobs.lever.co+{encoded_query}"
    return f"https://www.google.com/search?q={encoded_query}+jobs"


def search_link_jobs(config: SearchConfig) -> list[JobLead]:
    """Create apply-ready fallback rows when a source cannot be scraped safely.

    These rows are honest: they are search entrypoints, not scraped job postings.
    They still let the workbook/dashboard become the user's daily command center.
    """
    jobs: list[JobLead] = []
    for link in build_search_links(config):
        title = link.title or link.query
        location = link.location or "Canada"
        jobs.append(
            JobLead(
                title=f"{title.title()} search queue",
                company="Multiple employers",
                location=location,
                source=link.source,
                apply_url=link.url,
                description=f"Search queue for {link.query}. Open the apply link, pick a role, then paste/import the posting for tailoring.",
                source_job_id=f"search:{link.source}:{link.query}",
                notes="Fallback search link. Use when direct scraping is blocked or unavailable.",
            )
        )
    return dedupe_jobs(jobs)


def dedupe_jobs(jobs: list[JobLead]) -> list[JobLead]:
    seen: set[tuple[str, str, str, str]] = set()
    unique: list[JobLead] = []
    for job in jobs:
        key = (job.source.lower(), job.title.lower(), job.location.lower(), job.apply_url.lower())
        if key not in seen:
            seen.add(key)
            unique.append(job)
    return unique
