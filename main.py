"""
Main entry point / example usage.

Run with:
    python main.py

If LLM_API_KEY is set in the environment, every agent uses the
configured LLM provider for its reasoning step. Otherwise each agent
falls back to a deterministic offline heuristic, so the full pipeline
still runs end-to-end (useful for testing/demoing without a key).
"""

import json
import sys

from orchestrator import run_pipeline
from report import format_report

EXAMPLE_RESUME = """Name: Rahul
Education: B.Tech Computer Science
Experience: Software Engineering Intern at XYZ
Projects: Network Intrusion Detection System
Skills: Python, C++, SQL, Machine Learning, Git
"""

EXAMPLE_JOB_DESCRIPTION = """Senior Python Developer
Required: Python, SQL, Docker, AWS, Machine Learning, Git
"""


def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    if len(sys.argv) == 3:
        resume_text = load_text(sys.argv[1])
        job_text = load_text(sys.argv[2])
    else:
        print("(No resume/job files given — running the example from the spec.)\n")
        resume_text = EXAMPLE_RESUME
        job_text = EXAMPLE_JOB_DESCRIPTION

    result = run_pipeline(resume_text, job_text)

    print(format_report(result))

    # Also dump the raw structured data for anything downstream (a UI, an API, etc.)
    structured = {
        "candidate_profile": result.profile.to_dict(),
        "categorized_skills": result.skills.to_dict(),
        "job_requirements": result.job.to_dict(),
        "match_analysis": result.match.to_dict(),
        "gap_analysis": result.gaps.to_dict(),
        "recommendations": result.recommendations.to_dict(),
        "errors": result.errors,
    }
    with open("last_run_output.json", "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2)
    print("\n(Structured JSON also written to last_run_output.json)")


if __name__ == "__main__":
    main()
