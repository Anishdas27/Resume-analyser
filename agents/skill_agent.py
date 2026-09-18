"""Agent 2: Skill Extraction Agent — categorize and interpret skills."""

from llm_client import call_llm_json, LLMUnavailable
from schemas import CandidateProfile, CategorizedSkills

SYSTEM_PROMPT = """You are the Skill Extraction Agent in a multi-agent recruiting pipeline.
Given a candidate's structured profile, categorize their skills into a JSON object with keys:
programming_languages, databases, ai_ml_frameworks, tools_platforms, soft_skills, domain_expertise
(all lists of strings). Normalize synonyms/aliases to a canonical form (e.g. "ML" -> "Machine Learning",
"JS" -> "JavaScript", "Postgres"/"psql" -> "PostgreSQL"). Infer domain_expertise from projects/experience
when reasonable (e.g. "Network Intrusion Detection System" -> "Cybersecurity"). Do not invent skills that
have no basis in the profile. Return raw JSON only, no commentary, no markdown fences."""

# Canonical alias table used by the offline fallback (and as a normalization
# pass even when the LLM is used, to guard against inconsistent casing).
ALIASES = {
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "dl": "Deep Learning",
    "nlp": "Natural Language Processing",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "py": "Python",
    "python": "Python",
    "cpp": "C++",
    "c++": "C++",
    "postgres": "PostgreSQL",
    "psql": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "sql": "SQL",
    "aws": "AWS",
    "gcp": "GCP",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "git": "Git",
    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
}

PROGRAMMING_LANGS = {"Python", "C++", "Java", "JavaScript", "TypeScript", "C", "C#", "Go", "Rust", "R"}
DATABASES = {"SQL", "PostgreSQL", "MySQL", "MongoDB", "SQLite", "Redis"}
AI_ML = {"Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Natural Language Processing", "Scikit-learn"}
TOOLS = {"Git", "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Jenkins", "Linux"}


def normalize(skill: str) -> str:
    return ALIASES.get(skill.strip().lower(), skill.strip())


def _offline_fallback(profile: CandidateProfile) -> CategorizedSkills:
    result = CategorizedSkills()
    seen = set()
    all_raw = profile.technical_skills + profile.soft_skills
    for raw in all_raw:
        norm = normalize(raw)
        if norm in seen:
            continue
        seen.add(norm)
        if norm in PROGRAMMING_LANGS:
            result.programming_languages.append(norm)
        elif norm in DATABASES:
            result.databases.append(norm)
        elif norm in AI_ML:
            result.ai_ml_frameworks.append(norm)
        elif norm in TOOLS:
            result.tools_platforms.append(norm)
        else:
            result.soft_skills.append(norm)

    # Light domain inference from projects
    for project in profile.projects:
        low = project.lower()
        if "intrusion" in low or "security" in low:
            result.domain_expertise.append("Cybersecurity")
        elif "recommend" in low:
            result.domain_expertise.append("Recommendation Systems")

    return result


def run(profile: CandidateProfile) -> CategorizedSkills:
    try:
        data = call_llm_json(SYSTEM_PROMPT, f"CANDIDATE PROFILE:\n{profile.to_dict()}")
        return CategorizedSkills(
            programming_languages=[normalize(s) for s in data.get("programming_languages", [])],
            databases=[normalize(s) for s in data.get("databases", [])],
            ai_ml_frameworks=[normalize(s) for s in data.get("ai_ml_frameworks", [])],
            tools_platforms=[normalize(s) for s in data.get("tools_platforms", [])],
            soft_skills=data.get("soft_skills", []),
            domain_expertise=data.get("domain_expertise", []),
        )
    except LLMUnavailable:
        return _offline_fallback(profile)
