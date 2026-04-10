# Assessment 2 — Bug Reproducer & Fix Planner
## PurpleMerit AI/ML Engineer Assessment | April 2026

---

## What This Does
A multi-agent AI system that reads a bug report + logs, automatically
reproduces the bug with a runnable script, identifies the root cause,
and proposes a safe fix plan.

## Agent Flow
```
Orchestrator
   ├── Triage Agent        → extracts symptoms + hypotheses
   ├── Log Analyst Agent   → searches logs, extracts stack traces
   ├── Reproduction Agent  → generates + runs repro script
   ├── Fix Planner Agent   → root cause + patch plan
   └── Reviewer/Critic     → validates fix, edge cases
```

## Run on Mac
```bash
cd Assessment2_BugFixer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Run on Windows
```cmd
cd Assessment2_BugFixer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Optional LLM Mode
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key   # Mac
set ANTHROPIC_API_KEY=sk-ant-your-key      # Windows
python main.py
```

## Outputs
- `output/bug_analysis_latest.json`   ← full structured analysis
- `output/repro_test.py`              ← runnable repro script

## Run Repro Script Separately
```bash
cd output
python repro_test.py
# Expected: exits 1 with AttributeError (bug confirmed)
```

## Input Mode
Option A (Provided Mini-Repo) — mini_repo/session/manager.py
contains the intentionally introduced bug (async race condition).

## Traces
```bash
python main.py 2>&1 | tee output/trace.log
```
