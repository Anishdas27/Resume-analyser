# Multi-Agent Resume Analyzer & Job Matcher

A 5-agent pipeline that parses a resume, categorizes skills, matches against
a job description, analyzes skill gaps, and produces a final candidate-job
match report with actionable recommendations.

```
RESUME + JOB DESCRIPTION
   -> Resume Agent        (agents/resume_agent.py)
   -> Skill Agent         (agents/skill_agent.py)
   -> Job Match Agent     (agents/job_match_agent.py)
   -> Gap Agent           (agents/gap_agent.py)
   -> Recommendation Agent(agents/recommendation_agent.py)
   -> Final Report        (report.py)
```

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...   # optional — see below
```

## Run

```bash
python main.py                              # runs the example from the spec
python main.py my_resume.txt my_job.txt      # runs on your own files
```

## With vs. without an API key

Every agent calls the Claude API (`llm_client.py`) for its actual reasoning
step (parsing, categorizing, matching, prioritizing, recommending). If
`ANTHROPIC_API_KEY` is not set, each agent transparently falls back to a
deterministic offline heuristic (regex parsing, an alias table, exact-match
skill comparison) so the pipeline still runs end-to-end for testing/demoing
without a key or network access — just with less nuance than the LLM gives.

## Files

- `schemas.py` — dataclasses for every structure passed between agents
  (CandidateProfile, CategorizedSkills, JobRequirements, MatchAnalysis,
  GapAnalysis, Recommendations).
- `llm_client.py` — Claude API wrapper; JSON-in/JSON-out for every agent call.
- `agents/` — one file per agent, each exposing a `run(...)` function.
- `orchestrator.py` — chains the agents, catching per-agent failures so a
  partial resume or malformed job description degrades gracefully instead
  of crashing the whole run.
- `report.py` — formats the final structured result into the report shown
  in the spec (score bar, matching/missing skills, gaps, recommendations,
  interview prep, learning path).
- `main.py` — example usage / CLI entry point; also writes
  `last_run_output.json` with the full structured data.

## Extending

- **Skill aliases**: add entries to `ALIASES` in `agents/skill_agent.py`.
- **New resume formats** (PDF/DOCX): parse to plain text before calling
  `resume_agent.run()` — the agent itself only expects text in.
- **Different LLM / provider**: swap the implementation inside
  `llm_client.call_llm_json`; every agent only depends on that one function.
