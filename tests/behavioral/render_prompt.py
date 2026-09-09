#!/usr/bin/env python3
"""Render a self-contained decision scenario; never invoke a model or include grading."""
import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CASES = ("advisory_threshold", "explicit_budget", "worker_failure",
         "incomplete_milestone", "unforecast_assignment", "renamed_repair",
         "sparse_coverage", "austerity_correction")
SKILLS = ("austere-astra", "stingy-sol")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", required=True, choices=SKILLS)
    parser.add_argument("--case", required=True, choices=CASES)
    args = parser.parse_args()
    skill_dir = ROOT / "skills" / args.skill
    sources = [skill_dir / "SKILL.md", *(
        skill_dir / "references" / name
        for name in ("model-catalog.md", "orchestration.md", "cost-model.md",
                     "verification-contracts.md")
    ), ROOT / "tests" / "behavioral" / "cases" / f"{args.case}.md"]
    print("""You are the root orchestrator resuming the supplied project checkpoint.
Apply the supplied skill and references to the scenario. All project state, usage,
files, and worker reports below are synthetic fixtures, not your live environment.
Use only this packet. Do not inspect this repository, use live tools, spend a real
project budget, or actually spawn workers. Do not read any grading materials.

Execute the next decision step as an ordered JSON action trace. Actions are simulated
calls, not suggestions for a later conversation. You can inspect evidence, dispatch or
steer a worker, record task/milestone state, ask the user, or report status. Choose your
own action names and arguments. Include concrete ownership and verification when
assigning work. Do not invent results from actions that have not returned; stop the
trace at dependencies requiring new evidence. Independent actions may share a trace.
Return only JSON with:
  actions: [{action: string, arguments: object}]
  rationale: a short explanation grounded in the supplied facts
  user_message: the concise update you would send
Use at most six actions and about 600 words. This evaluates a single decision, not a
complete build. Record only actual runtime model/effort observations if exposed;
otherwise leave those unknown rather than treating the skill as runtime proof.
""")
    for path in sources:
        content = path.read_bytes()
        print(f"\n--- SOURCE {path.relative_to(ROOT)} sha256={hashlib.sha256(content).hexdigest()} ---")
        print(content.decode("utf-8"))


if __name__ == "__main__":
    main()
