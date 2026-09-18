# Resume Analyzer

A resume-to-job-description analysis pipeline that extracts a candidate profile, categorizes skills, identifies job requirements, evaluates the match, highlights skill gaps, and produces tailored recommendations.

## Current repository contents

The current upload includes the command-line entry point in `main.py`. It expects these pipeline modules to be present in the same project directory:

- `orchestrator.py` - runs the analysis pipeline
- `report.py` - formats the human-readable report
- Supporting model and analysis modules used by the orchestrator

Those supporting modules were not included in the uploaded files yet, so the repository is currently a scaffold and cannot run end-to-end until they are added.

## Intended features

- Parse resume text and job-description text
- Build a structured candidate profile
- Categorize technical and professional skills
- Extract job requirements
- Compare the candidate with the role
- Identify missing or weaker skills
- Generate actionable recommendations
- Export structured results to `last_run_output.json`
- Work offline with deterministic heuristics when `LLM_API_KEY` is not configured
- Optionally use a configured LLM provider for agent reasoning

## Usage

Run the example input:

```bash
python main.py
```

Analyze files by passing the resume first and the job description second:

```bash
python main.py path/to/resume.txt path/to/job_description.txt
```

The command prints a formatted report and writes structured output to `last_run_output.json`.

## Configuration

Set `LLM_API_KEY` in the environment to enable the configured LLM provider. Without it, the application is designed to use its offline heuristic fallback.

PowerShell:

```powershell
$env:LLM_API_KEY = "your-api-key"
python main.py
```

## Project status

This is the initial repository upload. Add the remaining pipeline and supporting modules before treating the project as a runnable release.
