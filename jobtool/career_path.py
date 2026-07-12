from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from jobtool.models import SearchConfig, _clean_lines
from jobtool.sources.search_links import DEFAULT_SOURCE_KEYS


@dataclass(frozen=True)
class CareerProfile:
    current_role: str
    target_roles: list[str]
    skills: list[str]
    interests: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)

    @classmethod
    def from_text(
        cls,
        current_role: str,
        target_roles_text: str,
        skills_text: str,
        interests_text: str = "",
        constraints_text: str = "",
    ) -> "CareerProfile":
        return cls(
            current_role=" ".join(current_role.strip().split()),
            target_roles=_clean_lines(target_roles_text),
            skills=_clean_lines(skills_text),
            interests=_clean_lines(interests_text),
            constraints=_clean_lines(constraints_text),
        )


@dataclass(frozen=True)
class RoadmapStep:
    stage: str
    action: str


@dataclass(frozen=True)
class RoleRecommendation:
    role: str
    fit_score: int
    why_it_fits: str
    matched_skills: list[str]
    missing_skills: list[str]
    roadmap: list[RoadmapStep]


@dataclass(frozen=True)
class CareerPlan:
    profile: CareerProfile
    recommendations: list[RoleRecommendation]
    search_config: SearchConfig


ROLE_CATALOG: dict[str, dict[str, list[str] | str]] = {
    "data analyst": {
        "label": "Data Analyst",
        "skills": ["SQL", "Excel", "Python", "Power BI", "Tableau", "statistics", "dashboards", "communication"],
        "signals": ["analytics", "dashboard", "reporting", "business", "healthcare", "finance"],
    },
    "business intelligence analyst": {
        "label": "Business Intelligence Analyst",
        "skills": ["SQL", "Power BI", "Tableau", "Excel", "data modeling", "ETL", "dashboards", "stakeholder communication"],
        "signals": ["bi", "business", "dashboard", "reporting", "metrics", "kpi"],
    },
    "bi analyst": {
        "label": "BI Analyst",
        "skills": ["SQL", "Power BI", "Tableau", "Excel", "data modeling", "dashboards", "stakeholder communication"],
        "signals": ["bi", "business", "dashboard", "reporting", "metrics", "kpi"],
    },
    "reporting analyst": {
        "label": "Reporting Analyst",
        "skills": ["SQL", "Excel", "Power BI", "reporting", "dashboards", "data quality", "communication"],
        "signals": ["report", "dashboard", "operations", "finance", "weekly", "monthly"],
    },
    "financial analyst": {
        "label": "Financial Analyst",
        "skills": ["Excel", "financial modeling", "SQL", "Power BI", "forecasting", "variance analysis", "communication"],
        "signals": ["finance", "budget", "forecast", "model", "accounting", "business"],
    },
    "machine learning engineer": {
        "label": "Machine Learning Engineer",
        "skills": ["Python", "machine learning", "statistics", "SQL", "model deployment", "APIs", "cloud", "MLOps"],
        "signals": ["ml", "machine learning", "ai", "model", "python", "automation"],
    },
}


def recommend_roles(profile: CareerProfile, limit: int = 5) -> list[RoleRecommendation]:
    requested = profile.target_roles or ["Data Analyst", "Business Intelligence Analyst", "Reporting Analyst"]
    recommendations = [_recommend_role(role, profile) for role in requested]
    recommendations.sort(key=lambda item: item.fit_score, reverse=True)
    return recommendations[:limit]


def build_career_plan(profile: CareerProfile, locations: list[str] | None = None) -> CareerPlan:
    recommendations = recommend_roles(profile)
    target_titles = profile.target_roles or [recommendation.role for recommendation in recommendations]
    search_config = SearchConfig(
        target_titles=target_titles,
        locations=locations or _locations_from_constraints(profile.constraints) or ["Toronto ON", "Remote Canada"],
        sources=DEFAULT_SOURCE_KEYS,
    )
    return CareerPlan(profile=profile, recommendations=recommendations, search_config=search_config)


def career_plan_to_dataframe(recommendations: list[RoleRecommendation]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Role": rec.role,
                "Fit score": rec.fit_score,
                "Why it fits": rec.why_it_fits,
                "Missing skills": ", ".join(rec.missing_skills),
                "Next actions": "\n".join(f"{step.stage}: {step.action}" for step in rec.roadmap),
            }
            for rec in recommendations
        ],
        columns=["Role", "Fit score", "Why it fits", "Missing skills", "Next actions"],
    )


def _recommend_role(role: str, profile: CareerProfile) -> RoleRecommendation:
    label, required_skills, signals = _catalog_entry(role)
    profile_skill_keys = {_normalize(skill) for skill in profile.skills}
    matched = [skill for skill in required_skills if _normalize(skill) in profile_skill_keys]
    missing = [skill for skill in required_skills if _normalize(skill) not in profile_skill_keys]

    interest_blob = " ".join(profile.interests + profile.constraints + [profile.current_role, role]).lower()
    signal_hits = sum(1 for signal in signals if signal.lower() in interest_blob)
    skill_score = int((len(matched) / max(len(required_skills), 1)) * 80)
    signal_score = min(signal_hits * 5, 20)
    target_bonus = 5 if any(_normalize(role) == _normalize(target) for target in profile.target_roles) else 0
    fit_score = min(100, skill_score + signal_score + target_bonus)

    why = _why_it_fits(label, matched, signal_hits, profile)
    roadmap = _roadmap(label, matched, missing)
    return RoleRecommendation(
        role=label,
        fit_score=fit_score,
        why_it_fits=why,
        matched_skills=matched,
        missing_skills=missing[:6],
        roadmap=roadmap,
    )


def _catalog_entry(role: str) -> tuple[str, list[str], list[str]]:
    key = _normalize(role)
    entry = ROLE_CATALOG.get(key)
    if not entry:
        return (
            " ".join(role.strip().split()).title(),
            ["Excel", "SQL", "communication", "portfolio project", "domain knowledge"],
            ["analytics", "business", "data", "operations"],
        )
    return str(entry["label"]), list(entry["skills"]), list(entry["signals"])


def _roadmap(role: str, matched: list[str], missing: list[str]) -> list[RoadmapStep]:
    first_missing = missing[:3]
    project_skills = matched[:3] + first_missing[:2]
    return [
        RoadmapStep("Week 1", f"Close the top skill gap: {', '.join(first_missing) if first_missing else 'document your strongest proof points'}"),
        RoadmapStep("Week 2", f"Build one {role} portfolio project using {', '.join(project_skills) if project_skills else 'realistic job data'}"),
        RoadmapStep("Week 3", f"Convert the project into resume bullets with tools, metric, business problem, and result"),
        RoadmapStep("Week 4", f"Generate a focused job queue for {role} and apply to the best-fit roles first"),
    ]


def _why_it_fits(role: str, matched: list[str], signal_hits: int, profile: CareerProfile) -> str:
    parts = []
    if matched:
        parts.append(f"You already show {', '.join(matched[:4])}.")
    else:
        parts.append("This is reachable, but your current skill proof is thin.")
    if signal_hits:
        parts.append("Your interests/constraints line up with the role direction.")
    if profile.current_role:
        parts.append(f"Current starting point: {profile.current_role}.")
    return " ".join(parts)


def _locations_from_constraints(constraints: list[str]) -> list[str]:
    locations = []
    for item in constraints:
        lowered = item.lower()
        if any(token in lowered for token in ["toronto", "remote", "canada", "vancouver", "halifax", "calgary"]):
            locations.append(item)
    return locations


def _normalize(value: str) -> str:
    return " ".join(value.lower().replace("/", " ").replace("-", " ").split())
