"""Agent 1: Resume Analysis Agent — parse & structure the raw resume text."""

import re
from llm_client import call_llm_json, LLMUnavailable
from schemas import CandidateProfile

SYSTEM_PROMPT = """You are the Resume Analysis Agent in a multi-agent recruiting pipeline.
Parse the raw resume text you are given and return ONLY a JSON object with these keys:
name (string or null), education (list of strings), work_experience (list of strings),
internships (list of strings), projects (list of strings), certifications (list of strings),
technical_skills (list of strings), soft_skills (list of strings), achievements (list of strings).
If a section is absent from the resume, return an empty list for it (never invent data).
Return raw JSON only, no commentary, no markdown fences."""


def _offline_fallback(resume_text: str) -> CandidateProfile:
    """Regex/heuristic parser used when no LLM is configured."""
    profile = CandidateProfile()

    name_match = re.search(r"Name\s*:\s*(.+)", resume_text, re.IGNORECASE)
    if name_match:
        profile.name = name_match.group(1).strip()

    section_map = {
        "education": ["education"],
        "work_experience": ["experience", "work experience"],
        "internships": ["internship", "internships"],
        "projects": ["project", "projects"],
        "certifications": ["certification", "certifications"],
        "technical_skills": ["skills", "technical skills"],
        "soft_skills": ["soft skills"],
        "achievements": ["achievements", "awards"],
    }

    lines = resume_text.splitlines()
    for line in lines:
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key_norm = key.strip().lower()
        value = value.strip()
        if not value:
            continue
        for field_name, aliases in section_map.items():
            if key_norm in aliases:
                items = [v.strip() for v in re.split(r",|;", value) if v.strip()]
                current = getattr(profile, field_name)
                current.extend(items if items else [value])
                setattr(profile, field_name, current)
                break

    return profile


def run(resume_text: str) -> CandidateProfile:
    """Returns a CandidateProfile parsed from raw resume text."""
    try:
        data = call_llm_json(SYSTEM_PROMPT, f"RESUME TEXT:\n{resume_text}")
        return CandidateProfile(
            name=data.get("name"),
            education=data.get("education", []),
            work_experience=data.get("work_experience", []),
            internships=data.get("internships", []),
            projects=data.get("projects", []),
            certifications=data.get("certifications", []),
            technical_skills=data.get("technical_skills", []),
            soft_skills=data.get("soft_skills", []),
            achievements=data.get("achievements", []),
        )
    except LLMUnavailable:
        return _offline_fallback(resume_text)
