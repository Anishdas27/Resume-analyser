"""
Shared data schemas for the multi-agent resume analyzer / job matcher.

Every agent takes structured input and returns a structured output that
conforms to one of these dataclasses (or a dict shaped like it, if you
don't want to depend on dataclasses at the call site).
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional


@dataclass
class CandidateProfile:
    name: Optional[str] = None
    education: List[str] = field(default_factory=list)
    work_experience: List[str] = field(default_factory=list)
    internships: List[str] = field(default_factory=list)
    projects: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    technical_skills: List[str] = field(default_factory=list)
    soft_skills: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class CategorizedSkills:
    programming_languages: List[str] = field(default_factory=list)
    databases: List[str] = field(default_factory=list)
    ai_ml_frameworks: List[str] = field(default_factory=list)
    tools_platforms: List[str] = field(default_factory=list)
    soft_skills: List[str] = field(default_factory=list)
    domain_expertise: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)

    def flat_technical(self) -> List[str]:
        return (
            self.programming_languages
            + self.databases
            + self.ai_ml_frameworks
            + self.tools_platforms
            + self.domain_expertise
        )


@dataclass
class JobRequirements:
    title: Optional[str] = None
    required_skills: List[str] = field(default_factory=list)
    raw_text: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class MatchAnalysis:
    matching_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    compatibility_percent: float = 0.0
    relevance_assessment: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SkillGap:
    skill: str
    priority: str  # HIGH, MEDIUM, LOW
    importance_rating: int  # 1-10


@dataclass
class GapAnalysis:
    gaps: List[SkillGap] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {"gaps": [asdict(g) for g in self.gaps]}


@dataclass
class Recommendations:
    overall_match_score: float = 0.0
    strongest_areas: List[str] = field(default_factory=list)
    weakest_areas: List[str] = field(default_factory=list)
    skills_to_learn: List[str] = field(default_factory=list)
    suggested_projects: List[str] = field(default_factory=list)
    resume_improvements: List[str] = field(default_factory=list)
    interview_prep_topics: List[str] = field(default_factory=list)
    learning_path: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)
