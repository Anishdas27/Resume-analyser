"""Agent 5: Recommendation Agent — generate actionable insights and the final report."""

from llm_client import call_llm_json, LLMUnavailable
from schemas import CandidateProfile, CategorizedSkills, JobRequirements, MatchAnalysis, GapAnalysis, Recommendations

SYSTEM_PROMPT = """You are the Recommendation Agent, the final stage of a multi-agent recruiting pipeline.
Given all prior agent outputs, return a JSON object with keys:
overall_match_score (number 0-100), strongest_areas (list of strings), weakest_areas (list of strings),
skills_to_learn (list of strings, ordered by priority), suggested_projects (list of strings, concrete
project ideas that would demonstrate the missing skills), resume_improvements (list of strings),
interview_prep_topics (list of strings), learning_path (list of strings, ordered step-by-step).
Be specific and actionable rather than generic. Return raw JSON only, no commentary, no markdown fences."""


def _offline_fallback(
    skills: CategorizedSkills, match: MatchAnalysis, gaps: GapAnalysis
) -> Recommendations:
    strongest = match.matching_skills[:5]
    weakest = [g.skill for g in gaps.gaps if g.priority == "HIGH"] or match.missing_skills[:3]
    skills_to_learn = [g.skill for g in sorted(gaps.gaps, key=lambda g: -g.importance_rating)]

    projects = [f"Build a project that applies {s} end-to-end" for s in skills_to_learn[:3]]
    improvements = [
        "Quantify impact in project/experience bullet points (metrics, scale, outcomes).",
        "Explicitly list missing high-priority skills you're actively learning, with a timeline.",
    ]
    interview_topics = skills_to_learn[:5] + ["System design basics relevant to the role"]
    learning_path = [f"Step {i+1}: Learn and build with {s}" for i, s in enumerate(skills_to_learn)]

    return Recommendations(
        overall_match_score=match.compatibility_percent,
        strongest_areas=strongest,
        weakest_areas=weakest,
        skills_to_learn=skills_to_learn,
        suggested_projects=projects,
        resume_improvements=improvements,
        interview_prep_topics=interview_topics,
        learning_path=learning_path,
    )


def run(
    profile: CandidateProfile,
    skills: CategorizedSkills,
    job: JobRequirements,
    match: MatchAnalysis,
    gaps: GapAnalysis,
) -> Recommendations:
    try:
        data = call_llm_json(
            SYSTEM_PROMPT,
            f"CANDIDATE PROFILE:\n{profile.to_dict()}\n\n"
            f"CATEGORIZED SKILLS:\n{skills.to_dict()}\n\n"
            f"JOB REQUIREMENTS:\n{job.to_dict()}\n\n"
            f"MATCH ANALYSIS:\n{match.to_dict()}\n\n"
            f"GAP ANALYSIS:\n{gaps.to_dict()}",
        )
        return Recommendations(
            overall_match_score=float(data.get("overall_match_score", match.compatibility_percent)),
            strongest_areas=data.get("strongest_areas", []),
            weakest_areas=data.get("weakest_areas", []),
            skills_to_learn=data.get("skills_to_learn", []),
            suggested_projects=data.get("suggested_projects", []),
            resume_improvements=data.get("resume_improvements", []),
            interview_prep_topics=data.get("interview_prep_topics", []),
            learning_path=data.get("learning_path", []),
        )
    except LLMUnavailable:
        return _offline_fallback(skills, match, gaps)
