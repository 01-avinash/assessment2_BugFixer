"""
main.py — Entry point for Assessment 2: Bug Reproducer & Fix Planner
Usage:  cd assessment2 && python main.py
Output: output/bug_analysis_latest.json  +  output/repro_test.py
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "agents"))

from agents import (
    TriageAgent,
    LogAnalystAgent,
    ReproductionAgent,
    FixPlannerAgent,
    ReviewerCriticAgent,
)

DATA_DIR   = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_bug_report() -> dict:
    with open(DATA_DIR / "bug_report.json") as f:
        return json.load(f)




def main():
    print("\n" + "🐛 " * 20)
    print("PURPLEMERIT — BUG REPRODUCER & FIX PLANNER")
    print("Assessment 2: Multi-Agent Bug Analysis System")
    print("🐛 " * 20 + "\n")

    if os.environ.get("ANTHROPIC_API_KEY"):
        print("✅ LLM Mode: Claude API key detected.\n")
    else:
        print("⚠️  Rule-based Mode: No API key — deterministic analysis.\n")

    bug_report = load_bug_report()
    print(f"📋 Bug: {bug_report['id']} — {bug_report['title']}\n")

    print("="*60)
    print("[ORCHESTRATOR] Starting 5-agent pipeline...")
    print("="*60)

    print("\n[ORCHESTRATOR] Step 1/5 → Triage Agent")
    triage = TriageAgent().analyze(bug_report)

    print("\n[ORCHESTRATOR] Step 2/5 → Log Analyst Agent")
    log_analysis = LogAnalystAgent().analyze()

    print("\n[ORCHESTRATOR] Step 3/5 → Reproduction Agent")
    repro = ReproductionAgent().generate_and_run(triage, log_analysis)

    print("\n[ORCHESTRATOR] Step 4/5 → Fix Planner Agent")
    fix_plan = FixPlannerAgent().plan(triage, log_analysis, repro)

    print("\n[ORCHESTRATOR] Step 5/5 → Reviewer/Critic Agent")
    review = ReviewerCriticAgent().review(triage, log_analysis, repro, fix_plan)

    print("\n[ORCHESTRATOR] Building final structured output...")

    final_output = {
        "bug_summary": {
            "id": bug_report["id"],
            "title": bug_report["title"],
            "severity": bug_report["severity"],
            "scope": triage["scope"],
            "affected_users": bug_report["affected_users"],
            "symptoms": triage["symptoms"],
        },
        "evidence": {
            "log_matches": {
                "null_user_id_warnings": log_analysis["null_user_id_warnings"],
                "auth_401_errors": log_analysis["auth_401_errors"],
                "attribute_errors": log_analysis["attribute_errors"],
                "stack_traces_found": log_analysis["stack_traces_found"],
            },
            "key_log_evidence": log_analysis["key_evidence"],
            "stack_trace_summary": log_analysis["stack_trace_summary"],
            "red_herrings_dismissed": log_analysis["red_herrings_dismissed"],
        },
        "repro_artifact": {
            "path": repro["repro_script_path"],
            "run_command": repro["run_command"],
            "expected_output": repro["expected_failing_output"],
            "bug_reproduced": repro["bug_reproduced"],
            "stdout_preview": repro["stdout_preview"],
        },
        "root_cause_hypothesis": fix_plan["root_cause"],
        "patch_plan": fix_plan["patch_plan"],
        "validation_plan": fix_plan["validation_plan"],
        "review": {
            "critique_summary": review["critique_summary"],
            "critiques": review["critiques"],
            "edge_cases": review["edge_cases"],
            "fix_safe_to_deploy": review["fix_safe_to_deploy"],
            "pre_deploy_checklist": review["pre_deploy_checklist"],
        },
        "open_questions": [
            "Are there other ensure_future() usages in the codebase?",
            "Do broken production sessions need a DB cleanup migration?",
            "What is the acceptable login latency budget post-fix?",
        ],
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"bug_analysis_{timestamp}.json"
    latest_file = OUTPUT_DIR / "bug_analysis_latest.json"

    with open(output_file, "w", encoding="utf-8") as f: # <--- ADDED encoding="utf-8"
        json.dump(final_output, f, indent=2)
    with open(latest_file, "w", encoding="utf-8") as f: # <--- ADDED encoding="utf-8"
        json.dump(final_output, f, indent=2)

    print("\n" + "="*60)
    print("FINAL STRUCTURED OUTPUT SUMMARY")
    print("="*60)
    print(json.dumps({
        "bug_id"         : final_output["bug_summary"]["id"],
        "severity"       : final_output["bug_summary"]["severity"],
        "root_cause"     : final_output["root_cause_hypothesis"]["hypothesis"],
        "confidence"     : final_output["root_cause_hypothesis"]["confidence"],
        "bug_reproduced" : final_output["repro_artifact"]["bug_reproduced"],
        "fix"            : final_output["patch_plan"]["one_line_fix"],
        "fix_safe"       : final_output["review"]["fix_safe_to_deploy"],
    }, indent=2))

    print(f"\n✅ Full output : {output_file}")
    print(f"✅ Latest      : {latest_file}")
    print(f"✅ Repro script: {repro['repro_script_path']}")
    print(f"\n▶  Run repro   : cd output && python repro_test.py")
    print(f"📝 Save traces : python main.py 2>&1 | tee output/trace.log")


if __name__ == "__main__":
    main()
