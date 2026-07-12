from __future__ import annotations

from urllib.parse import quote_plus

from jobtool.models import JobLead, SearchConfig, SearchLink

SOURCE_LABELS = {
    "linkedin": "LinkedIn",
    "indeed": "Indeed",
    "google_jobs": "Google Jobs",
    "canada_job_bank": "Canada Job Bank",
}


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
                if source == "linkedin":
                    url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_title}&location={encoded_location}"
                elif source == "indeed":
                    url = f"https://ca.indeed.com/jobs?q={encoded_title}&l={encoded_location}"
                elif source == "google_jobs":
                    url = f"https://www.google.com/search?q={encoded_query}+jobs"
                elif source == "canada_job_bank":
                    url = f"https://www.jobbank.gc.ca/jobsearch/jobsearch?searchstring={encoded_title}&locationstring={encoded_location}"
                else:
                    url = f"https://www.google.com/search?q={encoded_query}+jobs"
                links.append(SearchLink(source=label, query=query, url=url))
    return links


def search_link_jobs(config: SearchConfig) -> list[JobLead]:
    """Create apply-ready fallback rows when a source cannot be scraped safely.

    These rows are honest: they are search entrypoints, not scraped job postings.
    They still let the workbook/dashboard become the user's daily command center.
    """
    jobs: list[JobLead] = []
    for link in build_search_links(config):
        title = link.query.rsplit(" ", 1)[0]
        location = link.query.replace(title, "").strip() or "Canada"
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
