"""Agent 3: Job Matching Agent — compare candidate skills against job requirements."""

import re
from llm_client import call_llm_json, LLMUnavailable
from schemas import CategorizedSkills, JobRequirements, MatchAnalysis
from agents.skill_agent import normalize

SYSTEM_PROMPT = """You are the Job Matching Agent in a multi-agent recruiting pipeline.
Given the candidate's categorized skills and a job description, return a JSON object with keys:
matching_skills (list of strings — required job skills the candidate has, canonical names),
missing_skills (list of strings — required job skills the candidate lacks),
compatibility_percent (number 0-100 = matching/required * 100),
relevance_assessment (one paragraph string on overall fit).
Treat synonyms as equal (e.g. "ML" == "Machine Learning"). Base this only on the provided data.
Return raw JSON only, no commentary, no markdown fences."""


def parse_job_description(job_text: str) -> JobRequirements:
    """Extract a job title and a required-skills list from free-text JD."""
    title_match = re.search(r"^(.+)$", job_text.strip().splitlines()[0]) if job_text.strip() else None
    title = title_match.group(1).strip() if title_match else None

    required = []
    req_match = re.search(r"Required\s*:\s*(.+)", job_text, re.IGNORECASE)
    if req_match:
        required = [s.strip() for s in re.split(r",|;", req_match.group(1)) if s.strip()]

    return JobRequirements(title=title, required_skills=required, raw_text=job_text)


def _offline_fallback(skills: CategorizedSkills, job: JobRequirements) -> MatchAnalysis:
    candidate_norm = {normalize(s) for s in skills.flat_technical()}
    required_norm = [normalize(s) for s in job.required_skills]

    matching = [s for s in required_norm if s in candidate_norm]
    missing = [s for s in required_norm if s not in candidate_norm]
    pct = round(100 * len(matching) / len(required_norm), 1) if required_norm else 0.0

    assessment = (
        f"Candidate matches {len(matching)} of {len(required_norm)} required skills "
        f"({pct}% compatibility) for the {job.title or 'role'}."
    )
    return MatchAnalysis(
        matching_skills=matching,
        missing_skills=missing,
        compatibility_percent=pct,
        relevance_assessment=assessment,
    )


def run(skills: CategorizedSkills, job: JobRequirements) -> MatchAnalysis:
    try:
        data = call_llm_json(
            SYSTEM_PROMPT,
            f"CANDIDATE SKILLS:\n{skills.to_dict()}\n\nJOB DESCRIPTION:\n{job.raw_text}",
        )
        return MatchAnalysis(
            matching_skills=data.get("matching_skills", []),
            missing_skills=data.get("missing_skills", []),
            compatibility_percent=float(data.get("compatibility_percent", 0.0)),
            relevance_assessment=data.get("relevance_assessment", ""),
        )
    except LLMUnavailable:
        return _offline_fallback(skills, job)
