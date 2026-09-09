"""Replay the recorded 2026-09-08 incident against the amended controls.

The fixture holds the distilled per-thread counters, roles, and parent shape from
`austere-astra-postmortem-20260908-evidence.json`. Processed tokens are a resource
proxy, not dollars and not a weekly-allowance deduction. These tests check that the
controls would have produced a different decision; they do not re-run any project
work.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPTS = [ROOT / "skills" / name / "scripts" / "token_budget_guard.py"
           for name in ("stingy-sol", "austere-astra")]
INCIDENT = json.loads((ROOT / "tests" / "fixtures" / "incident-20260908.json").read_text())
CLASSES = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
           "output_tokens", "reasoning_output_tokens", "total_tokens")


def build_tree(directory, cutoff):
    """Write one JSONL session per thread that existed at `cutoff`."""
    sessions = directory / "sessions"
    sessions.mkdir(parents=True, exist_ok=True)
    written = 0
    for row in INCIDENT["threads"]:
        usage = row["at_stop"] if cutoff == "at_stop" else row["before_correction"]
        if not usage:
            continue
        meta = {"id": row["id"], "timestamp": "2026-09-07T20:00:00Z"}
        if row["parent"]:
            meta["parent_thread_id"] = row["parent"]
        if row["role"] == "guardian":
            meta["thread_source"] = "guardian_review"
            meta["source"] = {"subagent": {"other": "guardian"}}
        elif row["role"] == "worker":
            meta["thread_source"] = "subagent"
            meta["agent_path"] = row["agent_path"]
        rows = [{"type": "session_meta", "payload": meta},
                {"type": "turn_context",
                 "payload": {"model": row["model"], "effort": row["effort"]}},
                {"type": "token_usage_record",
                 "payload": {"thread_token_usage": {k: usage[k] for k in CLASSES}}}]
        (sessions / ("%s.jsonl" % row["id"])).write_text(
            "\n".join(json.dumps(item) for item in rows))
        written += 1
    return sessions / "root.jsonl", written


class IncidentReplayTests(unittest.TestCase):
    def guard(self, script, temp, cutoff, *args):
        root_path, _ = build_tree(Path(temp), cutoff)
        result = subprocess.run([sys.executable, str(script), "--cwd", temp, "--json",
                                 "--session", str(root_path), "--tree", *args],
                                capture_output=True, text=True)
        return result.returncode, json.loads(result.stdout)

    def test_fixture_matches_the_recorded_totals(self):
        summed = {key: sum(row["at_stop"][key] for row in INCIDENT["threads"])
                  for key in CLASSES}
        self.assertEqual(summed, INCIDENT["totals_at_stop"])
        self.assertEqual(INCIDENT["totals_at_stop"]["total_tokens"], 150009944)
        self.assertEqual(INCIDENT["totals_at_first_correction"]["total_tokens"], 9439808)
        self.assertEqual(INCIDENT["thread_counts"],
                         {"root": 1, "worker": 13, "guardian": 14})

    def test_all_three_roles_reconcile_to_the_tree_exactly_once(self):
        """M10: guardian overhead is inside the total and attributed to itself."""
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                _, body = self.guard(script, temp, "at_stop")
                self.assertEqual(body["thread_counts"],
                                 {"root": 1, "worker": 13, "guardian": 14})
                for role, expected in INCIDENT["role_totals_at_stop"].items():
                    self.assertEqual(body["roles"][role]["total_tokens"],
                                     expected["total_tokens"], role)
                self.assertEqual(
                    sum(body["roles"][role]["total_tokens"]
                        for role in ("root", "worker", "guardian")),
                    body["tokens"]["total_tokens"])
                self.assertEqual(body["tokens"]["total_tokens"], 150009944)
                self.assertEqual(body["roles"]["guardian"]["total_tokens"], 31351704)
                self.assertEqual(body["worker_tokens"]["total_tokens"], 98596406)

    def test_low_root_share_is_not_labelled_a_success(self):
        """M01: 13.4% root share with a 150M tree is not austerity."""
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                # a generous allowance: ten times the usage recorded at the first
                # correction, with modest reserves held back
                code, body = self.guard(script, temp, "at_stop",
                                        "--milestone", "dashboard-p1",
                                        "--allowance", "94398080",
                                        "--integration-reserve", "2000000",
                                        "--repair-reserve", "2000000",
                                        "--forecast", "1000")
                share = (body["roles"]["root"]["total_tokens"] /
                         body["tokens"]["total_tokens"])
                self.assertLess(share, 0.15)
                self.assertEqual(code, 40)
                self.assertEqual(body["action"], "resource_blocked")
                self.assertFalse(body["dispatch"]["eligible"])

    def test_repeated_thresholds_now_return_an_instruction(self):
        """M02: the guard no longer answers a crossed threshold with a number."""
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                code, body = self.guard(script, temp, "before_correction")
                self.assertEqual(code, 20)
                self.assertEqual(body["action"], "reduce_or_reframe")
                self.assertIn("declare a finite allowance", body["action_note"])

    def test_the_next_large_phase_cannot_be_unforecast(self):
        """M03 and G07: T4/T5-scale work needs an upper forecast to be eligible."""
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                code, body = self.guard(script, temp, "before_correction",
                                        "--milestone", "dashboard-p1",
                                        "--allowance", "40000000",
                                        "--integration-reserve", "2000000",
                                        "--repair-reserve", "2000000",
                                        "--forecast", "unknown")
                self.assertEqual(code, 25)
                self.assertEqual(body["action"], "bounded_diagnostic")
                self.assertFalse(body["dispatch"]["eligible"])
                # the actual T4 gate worker alone would not have fit that headroom
                t4 = next(row for row in INCIDENT["threads"]
                          if row["agent_path"] == "/root/t4_observer_gate")
                self.assertGreater(t4["at_stop"]["total_tokens"],
                                   body["milestone"]["headroom"])

    def test_usage_after_the_first_correction_is_incremental_and_visible(self):
        """M09 and M11: the post-correction growth is measured, not re-derived."""
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                ledger = Path(temp) / "milestone.json"
                base = Path(temp) / "correction"
                stop = Path(temp) / "stop"
                root_before, _ = build_tree(base, "before_correction")
                root_after, _ = build_tree(stop, "at_stop")
                subprocess.run([sys.executable, str(script), "--cwd", str(base),
                                "--json", "--session", str(root_before), "--tree",
                                "--ledger", str(ledger), "--milestone", "dashboard-p1",
                                "--allowance", "40000000", "--snapshot",
                                "first_user_correction"], capture_output=True, text=True)
                result = subprocess.run(
                    [sys.executable, str(script), "--cwd", str(stop), "--json",
                     "--session", str(root_after), "--tree", "--ledger", str(ledger),
                     "--forecast", "1000"], capture_output=True, text=True)
                body = json.loads(result.stdout)
                self.assertEqual(body["milestone"]["baseline_total_tokens"], 9439808)
                self.assertEqual(body["milestone"]["spent"], 140570136)
                self.assertEqual(body["milestone"]["incremental_since_last_snapshot"],
                                 140570136)
                self.assertEqual(result.returncode, 40)
                self.assertEqual(body["dispatch"]["decision"], "resource_blocked")

    def test_renamed_repair_cannot_reset_the_ledger(self):
        """G02: the T6a-style rename keeps the same milestone accounting."""
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                ledger = Path(temp) / "milestone.json"
                root_path, _ = build_tree(Path(temp), "at_stop")
                subprocess.run([sys.executable, str(script), "--cwd", temp, "--json",
                                "--session", str(root_path), "--tree", "--ledger",
                                str(ledger), "--milestone", "dashboard-p1",
                                "--allowance", "40000000", "--snapshot", "stop"],
                               capture_output=True, text=True)
                result = subprocess.run(
                    [sys.executable, str(script), "--cwd", temp, "--json", "--session",
                     str(root_path), "--tree", "--ledger", str(ledger), "--milestone",
                     "dashboard-p1-t6b", "--forecast", "1000"],
                    capture_output=True, text=True)
                self.assertEqual(result.returncode, 30)
                self.assertEqual(json.loads(result.stdout)["status"], "invalid")

    def test_effective_routing_shows_the_unexamined_high_effort_pattern(self):
        """M04: 12 of 13 workers at high effort is recorded, and reviewable."""
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                _, body = self.guard(script, temp, "at_stop")
                workers = [entry for entry in body["routing"].values()
                           if entry["role"] == "worker"]
                self.assertEqual(len(workers), 13)
                self.assertEqual(sum(1 for entry in workers
                                     if entry["effective_effort"] == "high"), 12)
                self.assertEqual(sum(1 for entry in workers
                                     if entry["effective_effort"] in ("low", "none")), 0)
                self.assertTrue(all(entry["agent_path"] for entry in workers))

    def test_one_worker_dominating_the_tree_is_visible_per_thread(self):
        """M03: the T4 gate worker alone was 21.6% of the measured tree."""
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                _, body = self.guard(script, temp, "at_stop")
                t4 = next(row for row in INCIDENT["threads"]
                          if row["agent_path"] == "/root/t4_observer_gate")
                observed = body["thread_tokens"][t4["id"]]["total_tokens"]
                self.assertEqual(observed, 32461094)
                self.assertGreater(observed / body["tokens"]["total_tokens"], 0.21)


if __name__ == "__main__":
    unittest.main()
