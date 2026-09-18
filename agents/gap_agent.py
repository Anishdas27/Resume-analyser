"""Agent 4: Skill Gap Analysis Agent — identify and prioritize missing skills."""

from llm_client import call_llm_json, LLMUnavailable
from schemas import CandidateProfile, JobRequirements, MatchAnalysis, GapAnalysis, SkillGap

SYSTEM_PROMPT = """You are the Skill Gap Analysis Agent in a multi-agent recruiting pipeline.
Given the candidate profile, job requirements, and match analysis, return a JSON object with key
"gaps": a list of objects, each with "skill" (string), "priority" ("HIGH"|"MEDIUM"|"LOW"),
and "importance_rating" (integer 1-10). Prioritize skills that are foundational to the role or
appear central to the job description as HIGH. Return raw JSON only, no commentary, no markdown fences."""

# Skills commonly considered "foundational" for a role get bumped to HIGH priority
# in the offline heuristic (crude but deterministic stand-in for LLM judgment).
FOUNDATIONAL_HINTS = {"docker", "aws", "kubernetes", "sql", "python", "cloud", "linux"}


def _offline_fallback(match: MatchAnalysis) -> GapAnalysis:
    gaps = []
    for skill in match.missing_skills:
        is_foundational = skill.lower() in FOUNDATIONAL_HINTS
        priority = "HIGH" if is_foundational else "MEDIUM"
        rating = 8 if is_foundational else 5
        gaps.append(SkillGap(skill=skill, priority=priority, importance_rating=rating))
    return GapAnalysis(gaps=gaps)


def run(profile: CandidateProfile, job: JobRequirements, match: MatchAnalysis) -> GapAnalysis:
    try:
        data = call_llm_json(
            SYSTEM_PROMPT,
            f"CANDIDATE PROFILE:\n{profile.to_dict()}\n\n"
            f"JOB REQUIREMENTS:\n{job.to_dict()}\n\n"
            f"MATCH ANALYSIS:\n{match.to_dict()}",
        )
        gaps = [
            SkillGap(
                skill=g["skill"],
                priority=g.get("priority", "MEDIUM"),
                importance_rating=int(g.get("importance_rating", 5)),
            )
            for g in data.get("gaps", [])
        ]
        return GapAnalysis(gaps=gaps)
    except LLMUnavailable:
        return _offline_fallback(match)
