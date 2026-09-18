"""Formats a PipelineResult into the final human-readable candidate-job match report."""

from orchestrator import PipelineResult


def _score_bar(pct: float, width: int = 20) -> str:
    filled = round(width * max(0, min(pct, 100)) / 100)
    return "█" * filled + "░" * (width - filled)


def format_report(result: PipelineResult) -> str:
    p, s, j, m, g, r = (
        result.profile,
        result.skills,
        result.job,
        result.match,
        result.gaps,
        result.recommendations,
    )

    lines = []
    lines.append("=" * 60)
    lines.append("CANDIDATE-JOB MATCH REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Candidate: {p.name or 'Unknown'}")
    lines.append(f"Role: {j.title or 'Unspecified role'}")
    lines.append("")
    lines.append("EXECUTIVE SUMMARY")
    lines.append("-" * 60)
    lines.append(f"Overall Match Score: {r.overall_match_score:.0f}%  {_score_bar(r.overall_match_score)}")
    lines.append(m.relevance_assessment)
    lines.append("")

    lines.append(f"MATCHING SKILLS ({len(m.matching_skills)}/{len(m.matching_skills) + len(m.missing_skills)})")
    lines.append("-" * 60)
    for skill in m.matching_skills:
        lines.append(f"  ✓ {skill}")
    lines.append("")

    lines.append(f"MISSING REQUIREMENTS ({len(m.missing_skills)})")
    lines.append("-" * 60)
    gap_priority = {gap.skill: gap.priority for gap in g.gaps}
    for skill in m.missing_skills:
        priority = gap_priority.get(skill, "MEDIUM")
        lines.append(f"  ✗ {skill} ({priority} priority)")
    lines.append("")

    lines.append("SKILL GAP DETAIL")
    lines.append("-" * 60)
    for gap in sorted(g.gaps, key=lambda x: -x.importance_rating):
        lines.append(f"  [{gap.priority:>6}] {gap.skill} — importance {gap.importance_rating}/10")
    lines.append("")

    lines.append("STRONGEST AREAS")
    lines.append("-" * 60)
    for area in r.strongest_areas:
        lines.append(f"  • {area}")
    lines.append("")

    lines.append("WEAKEST AREAS")
    lines.append("-" * 60)
    for area in r.weakest_areas:
        lines.append(f"  • {area}")
    lines.append("")

    lines.append("RECOMMENDATIONS")
    lines.append("-" * 60)
    for i, rec in enumerate([
        *[f"Learn: {sk}" for sk in r.skills_to_learn],
        *r.suggested_projects,
        *r.resume_improvements,
    ], start=1):
        lines.append(f"  {i}. {rec}")
    lines.append("")

    lines.append("INTERVIEW PREPARATION TOPICS")
    lines.append("-" * 60)
    for topic in r.interview_prep_topics:
        lines.append(f"  • {topic}")
    lines.append("")

    lines.append("LEARNING PATH")
    lines.append("-" * 60)
    for step in r.learning_path:
        lines.append(f"  → {step}")
    lines.append("")

    if result.errors:
        lines.append("NOTES / WARNINGS")
        lines.append("-" * 60)
        for err in result.errors:
            lines.append(f"  ! {err}")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)
