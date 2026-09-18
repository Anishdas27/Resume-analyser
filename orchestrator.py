"""
Pipeline orchestration: chains the 5 agents sequentially, passing each
agent's structured output as the next agent's input. Each stage is
wrapped so a failure in one agent doesn't crash the whole run — it logs
the error and substitutes an empty/default result, so a partial resume
or a weird job description degrades gracefully instead of throwing.
"""

from dataclasses import dataclass

from schemas import (
    CandidateProfile,
    CategorizedSkills,
    JobRequirements,
    MatchAnalysis,
    GapAnalysis,
    Recommendations,
)
from agents import resume_agent, skill_agent, job_match_agent, gap_agent, recommendation_agent


@dataclass
class PipelineResult:
    profile: CandidateProfile
    skills: CategorizedSkills
    job: JobRequirements
    match: MatchAnalysis
    gaps: GapAnalysis
    recommendations: Recommendations
    errors: list


def run_pipeline(resume_text: str, job_description_text: str) -> PipelineResult:
    errors = []

    if not resume_text or not resume_text.strip():
        errors.append("Resume text is empty — proceeding with a blank candidate profile.")
        profile = CandidateProfile()
    else:
        try:
            profile = resume_agent.run(resume_text)
        except Exception as e:
            errors.append(f"Resume Agent failed: {e}")
            profile = CandidateProfile()

    try:
        skills = skill_agent.run(profile)
    except Exception as e:
        errors.append(f"Skill Agent failed: {e}")
        skills = CategorizedSkills()

    try:
        job = job_match_agent.parse_job_description(job_description_text)
    except Exception as e:
        errors.append(f"Job description parsing failed: {e}")
        job = JobRequirements(raw_text=job_description_text)

    if not job.required_skills:
        errors.append("No required skills detected in job description — match score may be 0%.")

    try:
        match = job_match_agent.run(skills, job)
    except Exception as e:
        errors.append(f"Job Match Agent failed: {e}")
        match = MatchAnalysis()

    try:
        gaps = gap_agent.run(profile, job, match)
    except Exception as e:
        errors.append(f"Gap Agent failed: {e}")
        gaps = GapAnalysis()

    try:
        recommendations = recommendation_agent.run(profile, skills, job, match, gaps)
    except Exception as e:
        errors.append(f"Recommendation Agent failed: {e}")
        recommendations = Recommendations()

    return PipelineResult(
        profile=profile,
        skills=skills,
        job=job,
        match=match,
        gaps=gaps,
        recommendations=recommendations,
        errors=errors,
    )
