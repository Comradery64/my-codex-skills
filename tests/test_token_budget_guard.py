import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPTS = [ROOT / "skills" / name / "scripts" / "token_budget_guard.py"
           for name in ("stingy-sol", "austere-astra")]


def write(path, sid, parent=None, usage=(0,), cumulative=True,
          timestamp="2026-01-01T00:00:00Z", role=None, model=None, effort=None,
          agent_path=None):
    meta = {"id": sid, "timestamp": timestamp}
    if parent:
        meta["parent_thread_id"] = parent
    if role == "guardian":
        meta["thread_source"] = "guardian_review"
        meta["source"] = {"subagent": {"other": "guardian"}}
    elif role == "worker":
        meta["thread_source"] = "subagent"
        meta["source"] = {"subagent": {"thread_spawn": {"agent_path": agent_path}}}
        meta["agent_path"] = agent_path
    rows = [{"type": "session_meta", "payload": meta},
            {"type": "turn_context", "payload": {"model": model, "effort": effort}}]
    running = 0
    for amount in usage:
        running += amount
        current = {"input_tokens": amount, "total_tokens": amount}
        payload = {"usage": current}
        if cumulative:
            payload["thread_token_usage"] = {"input_tokens": running, "total_tokens": running}
        rows.append({"type": "token_usage_record", "payload": payload})
    rows.append({"type": "response_item", "payload": {"message": "TOP_SECRET_SENTINEL"}})
    path.write_text("{malformed\n" + "\n".join(json.dumps(row) for row in rows))


class GuardTests(unittest.TestCase):
    def run_guard(self, script, root, *args):
        return subprocess.run([sys.executable, str(script), "--cwd", str(root),
                               "--json", *args], capture_output=True, text=True)

    def test_skill_copies_are_identical(self):
        self.assertEqual(SCRIPTS[0].read_bytes(), SCRIPTS[1].read_bytes())

    def test_tree_sums_each_thread_once(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                sessions = Path(temp) / "sessions"; sessions.mkdir()
                write(sessions / "root.jsonl", "root", usage=(100, 200))
                write(sessions / "child.jsonl", "child", "root", usage=(200,))
                result = self.run_guard(script, temp, "--session", str(sessions / "root.jsonl"),
                                        "--tree", "--soft-limit", "450", "--hard-limit", "450")
                body = json.loads(result.stdout)
                self.assertEqual(result.returncode, 20)
                self.assertEqual(body["tokens"]["total_tokens"], 500)
                self.assertEqual(body["threads"], 2)
                self.assertEqual(body["turns"], 2)
                self.assertEqual(set(body["thread_sources"]), {"root", "child"})
                self.assertNotIn("TOP_SECRET_SENTINEL", result.stdout)

    def test_without_tree_uses_only_selected_thread(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                sessions = Path(temp) / "sessions"; sessions.mkdir()
                write(sessions / "root.jsonl", "root", usage=(100, 200))
                write(sessions / "child.jsonl", "child", "root", usage=(200,))
                result = self.run_guard(script, temp, "--session", str(sessions / "root.jsonl"),
                                        "--soft-limit", "400", "--hard-limit", "450")
                body = json.loads(result.stdout)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(body["tokens"]["total_tokens"], 300)
                self.assertEqual(body["threads"], 1)

    def test_tree_with_missing_child_usage_is_unknown(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                sessions = Path(temp) / "sessions"; sessions.mkdir()
                write(sessions / "root.jsonl", "root", usage=(100,))
                child = [{"type": "session_meta", "payload": {
                    "id": "child", "parent_thread_id": "root",
                    "timestamp": "2026-01-01T00:00:00Z"}}]
                (sessions / "child.jsonl").write_text("\n".join(json.dumps(row) for row in child))
                result = self.run_guard(script, temp, "--session", str(sessions / "root.jsonl"),
                                        "--tree")
                body = json.loads(result.stdout)
                self.assertEqual(result.returncode, 30)
                self.assertEqual(body["status"], "unknown")
                self.assertEqual(body["action"], "aggregate_unavailable")
                self.assertEqual(body["missing_threads"], ["child"])
                self.assertEqual(body["thread_tokens"], {
                    "child": None,
                    "root": {"cache_write_input_tokens": 0, "cached_input_tokens": 0,
                             "input_tokens": 100, "output_tokens": 0,
                             "reasoning_output_tokens": 0, "total_tokens": 100},
                })
                self.assertEqual(body["root_tokens"]["total_tokens"], 100)
                self.assertIsNone(body["worker_tokens"])
                self.assertTrue(body["unavailable_fields"])

    def test_tree_breakdown_includes_descendants_only_once(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                sessions = Path(temp) / "sessions"; sessions.mkdir()
                write(sessions / "root.jsonl", "root", usage=(100,))
                write(sessions / "child.jsonl", "child", "root", usage=(20,))
                write(sessions / "grandchild.jsonl", "grandchild", "child", usage=(3,))
                write(sessions / "unrelated.jsonl", "unrelated", usage=(999,))
                result = self.run_guard(script, temp, "--session", str(sessions / "root.jsonl"),
                                        "--tree")
                body = json.loads(result.stdout)
                self.assertEqual(body["root_tokens"]["total_tokens"], 100)
                self.assertEqual(body["worker_tokens"]["total_tokens"], 23)
                self.assertEqual(set(body["thread_tokens"]), {"root", "child", "grandchild"})
                self.assertEqual(body["tokens"]["total_tokens"], 123)

    def test_without_tree_reports_zero_worker_tokens(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                sessions = Path(temp) / "sessions"; sessions.mkdir()
                write(sessions / "root.jsonl", "root", usage=(100,))
                write(sessions / "child.jsonl", "child", "root", usage=(20,))
                result = self.run_guard(script, temp, "--session", str(sessions / "root.jsonl"))
                body = json.loads(result.stdout)
                self.assertEqual(body["worker_tokens"], {
                    "cache_write_input_tokens": 0, "cached_input_tokens": 0,
                    "input_tokens": 0, "output_tokens": 0,
                    "reasoning_output_tokens": 0, "total_tokens": 0,
                })
                self.assertEqual(set(body["thread_tokens"]), {"root"})

    def test_request_usage_fallback_and_thresholds(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                sessions = Path(temp) / "sessions"; sessions.mkdir()
                write(sessions / "root.jsonl", "root", usage=(40, 60), cumulative=False)
                result = self.run_guard(script, temp, "--soft-limit", "100")
                body = json.loads(result.stdout)
                self.assertEqual(result.returncode, 10)
                self.assertEqual(body["tokens"]["total_tokens"], 100)
                self.assertEqual(body["aggregate_source"], "sum(payload.usage)")

    def test_newest_root_and_unknown_exit(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                sessions = Path(temp) / "sessions"; sessions.mkdir()
                write(sessions / "old.jsonl", "old", usage=(1,), timestamp="2026-01-01T00:00:00Z")
                write(sessions / "new.jsonl", "new", usage=(2,), timestamp="2026-01-02T00:00:00Z")
                result = self.run_guard(script, temp)
                self.assertEqual(json.loads(result.stdout)["session"], "new")
            with self.subTest(script=script, case="unknown"), tempfile.TemporaryDirectory() as temp:
                result = self.run_guard(script, temp)
                self.assertEqual(result.returncode, 30)
                self.assertEqual(json.loads(result.stdout)["status"], "unknown")


class RoleAttributionTests(unittest.TestCase):
    """M10: guardians are their own role inside the same reconciled total."""

    def tree(self, temp):
        sessions = Path(temp) / "sessions"; sessions.mkdir()
        write(sessions / "root.jsonl", "root", usage=(100,), model="gpt-6-astra",
              effort="xhigh")
        write(sessions / "w1.jsonl", "w1", "root", usage=(40,), role="worker",
              model="gpt-5.6-terra", effort="high", agent_path="/root/t1")
        # a guardian hangs off the thread it reviews, not off the root
        write(sessions / "g1.jsonl", "g1", "w1", usage=(7,), role="guardian",
              model="codex-auto-review", effort="low")
        return sessions

    def run_guard(self, script, root, *args):
        return subprocess.run([sys.executable, str(script), "--cwd", str(root),
                               "--json", *args], capture_output=True, text=True)

    def test_roles_reconcile_exactly_once(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                sessions = self.tree(temp)
                body = json.loads(self.run_guard(
                    script, temp, "--session", str(sessions / "root.jsonl"),
                    "--tree").stdout)
                roles = body["roles"]
                self.assertEqual(roles["root"]["total_tokens"], 100)
                self.assertEqual(roles["worker"]["total_tokens"], 40)
                self.assertEqual(roles["guardian"]["total_tokens"], 7)
                self.assertEqual(sum(roles[r]["total_tokens"] for r in
                                     ("root", "worker", "guardian")),
                                 body["tokens"]["total_tokens"])
                self.assertEqual(body["thread_counts"],
                                 {"root": 1, "worker": 1, "guardian": 1})

    def test_guardian_usage_is_not_charged_to_workers(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                sessions = self.tree(temp)
                body = json.loads(self.run_guard(
                    script, temp, "--session", str(sessions / "root.jsonl"),
                    "--tree").stdout)
                self.assertEqual(body["worker_tokens"]["total_tokens"], 40)
                self.assertEqual(body["thread_roles"]["g1"], "guardian")

    def test_effective_routing_is_recorded(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                sessions = self.tree(temp)
                body = json.loads(self.run_guard(
                    script, temp, "--session", str(sessions / "root.jsonl"),
                    "--tree").stdout)
                self.assertEqual(body["routing"]["w1"], {
                    "role": "worker", "agent_path": "/root/t1",
                    "effective_model": "gpt-5.6-terra", "effective_effort": "high"})
                self.assertEqual(body["enforcement"],
                                 "dispatch_boundary_and_cooperative")


class DispatchDecisionTests(unittest.TestCase):
    """M02 and the section-4 dispatch contract: thresholds return instructions."""

    def run_guard(self, script, root, *args):
        return subprocess.run([sys.executable, str(script), "--cwd", str(root),
                               "--json", *args], capture_output=True, text=True)

    def session(self, temp, total):
        sessions = Path(temp) / "sessions"; sessions.mkdir()
        write(sessions / "root.jsonl", "root", usage=(total,))
        return sessions / "root.jsonl"

    def guard(self, script, temp, total, *args):
        path = self.session(temp, total)
        result = self.run_guard(script, temp, "--session", str(path), *args)
        return result.returncode, json.loads(result.stdout)

    def test_default_checkpoint_still_names_an_action(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                code, body = self.guard(script, temp, 300000)
                self.assertEqual(code, 20)
                self.assertEqual(body["action"], "reduce_or_reframe")
                self.assertIn("declare a finite allowance", body["action_note"])

    def test_forecast_within_headroom_proceeds(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                code, body = self.guard(script, temp, 400000, "--milestone", "m1",
                                        "--allowance", "1000000",
                                        "--integration-reserve", "100000",
                                        "--repair-reserve", "100000",
                                        "--forecast", "200000")
                self.assertEqual(code, 0)
                self.assertEqual(body["dispatch"]["decision"], "proceed_within_allowance")
                self.assertTrue(body["dispatch"]["eligible"])
                # with no baseline snapshot, the whole tree total counts as spent
                self.assertEqual(body["milestone"]["spent"], 400000)
                self.assertEqual(body["milestone"]["headroom"], 400000)

    def test_oversized_forecast_cannot_enter_dispatch(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                code, body = self.guard(script, temp, 400000, "--milestone", "m1",
                                        "--allowance", "1000000",
                                        "--integration-reserve", "100000",
                                        "--repair-reserve", "100000",
                                        "--forecast", "900000")
                self.assertEqual(code, 20)
                self.assertEqual(body["dispatch"]["decision"], "reduce_or_reframe")
                self.assertFalse(body["dispatch"]["eligible"])
                self.assertIn("do not raise the allowance", body["dispatch"]["reason"])

    def test_unforecast_assignment_gets_only_a_bounded_diagnostic(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                code, body = self.guard(script, temp, 100000, "--milestone", "m1",
                                        "--allowance", "1000000",
                                        "--forecast", "unknown")
                self.assertEqual(code, 25)
                self.assertEqual(body["dispatch"]["decision"], "bounded_diagnostic")
                self.assertFalse(body["dispatch"]["eligible"])

    def test_exhausted_reserves_block_dispatch(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                code, body = self.guard(script, temp, 950000, "--milestone", "m1",
                                        "--allowance", "1000000",
                                        "--integration-reserve", "100000",
                                        "--repair-reserve", "100000",
                                        "--forecast", "1000")
                self.assertEqual(code, 40)
                self.assertEqual(body["dispatch"]["decision"], "resource_blocked")
                self.assertIn("report the resource blocker", body["dispatch"]["reason"])

    def test_missing_allowance_is_invalid_not_unlimited(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                code, body = self.guard(script, temp, 300000, "--milestone", "m1",
                                        "--forecast", "10")
                self.assertEqual(code, 10)
                self.assertIsNone(body["milestone"]["allowance"])
                self.assertIn("invalid, not unlimited", body["action_note"])


class MilestoneLedgerTests(unittest.TestCase):
    """G02: renaming a repair or rotating a worker never resets accounting."""

    def run_guard(self, script, root, *args):
        return subprocess.run([sys.executable, str(script), "--cwd", str(root),
                               "--json", *args], capture_output=True, text=True)

    def build(self, temp, total):
        sessions = Path(temp) / "sessions"
        if not sessions.exists():
            sessions.mkdir()
        write(sessions / "root.jsonl", "root", usage=(total,))
        return sessions / "root.jsonl"

    def test_snapshot_reports_incremental_usage(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                ledger = Path(temp) / "milestone.json"
                path = self.build(temp, 100000)
                self.run_guard(script, temp, "--session", str(path), "--ledger",
                               str(ledger), "--milestone", "p1", "--allowance",
                               "1000000", "--snapshot", "start")
                path = self.build(temp, 640000)
                body = json.loads(self.run_guard(
                    script, temp, "--session", str(path), "--ledger", str(ledger),
                    "--forecast", "1000").stdout)
                self.assertEqual(body["milestone"]["baseline_total_tokens"], 100000)
                self.assertEqual(body["milestone"]["spent"], 540000)
                self.assertEqual(body["milestone"]["incremental_since_last_snapshot"],
                                 540000)
                self.assertEqual(body["milestone"]["allowance"], 1000000)

    def test_renaming_the_milestone_is_refused(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                ledger = Path(temp) / "milestone.json"
                path = self.build(temp, 100000)
                self.run_guard(script, temp, "--session", str(path), "--ledger",
                               str(ledger), "--milestone", "p1", "--allowance",
                               "1000000", "--snapshot", "start")
                result = self.run_guard(script, temp, "--session", str(path),
                                        "--ledger", str(ledger), "--milestone",
                                        "p1-repair-take-2", "--forecast", "1000")
                body = json.loads(result.stdout)
                self.assertEqual(result.returncode, 30)
                self.assertEqual(body["status"], "invalid")
                self.assertIn("reuse the stable ID", body["error"])

    def test_allowance_cannot_be_resized_to_fit(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                ledger = Path(temp) / "milestone.json"
                path = self.build(temp, 900000)
                self.run_guard(script, temp, "--session", str(path), "--ledger",
                               str(ledger), "--milestone", "p1", "--allowance",
                               "1000000", "--snapshot", "start")
                result = self.run_guard(script, temp, "--session", str(path),
                                        "--ledger", str(ledger), "--allowance",
                                        "9000000", "--forecast", "1000")
                body = json.loads(result.stdout)
                self.assertEqual(result.returncode, 30)
                self.assertIn("never resize it", body["error"])

    def test_ledger_snapshots_are_append_only(self):
        for script in SCRIPTS:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                ledger = Path(temp) / "milestone.json"
                for total, label in ((100000, "start"), (200000, "wave1"),
                                     (300000, "wave2")):
                    path = self.build(temp, total)
                    self.run_guard(script, temp, "--session", str(path), "--ledger",
                                   str(ledger), "--milestone", "p1", "--allowance",
                                   "1000000", "--snapshot", label)
                saved = json.loads(ledger.read_text())
                self.assertEqual([s["label"] for s in saved["snapshots"]],
                                 ["start", "wave1", "wave2"])
                self.assertEqual(saved["milestone_id"], "p1")


if __name__ == "__main__":
    unittest.main()
