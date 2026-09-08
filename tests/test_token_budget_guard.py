import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPTS = [ROOT / "skills" / name / "scripts" / "token_budget_guard.py"
           for name in ("stingy-sol", "austere-astra")]


def write(path, sid, parent=None, usage=(0,), cumulative=True, timestamp="2026-01-01T00:00:00Z"):
    rows = [{"type": "session_meta", "payload": {"id": sid, "timestamp": timestamp,
             **({"parent_thread_id": parent} if parent else {})}},
            {"type": "turn_context", "payload": {}}]
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
                self.assertEqual(body["missing_threads"], ["child"])
                self.assertEqual(body["thread_tokens"], {
                    "child": None,
                    "root": {"cache_write_input_tokens": 0, "cached_input_tokens": 0,
                             "input_tokens": 100, "output_tokens": 0,
                             "reasoning_output_tokens": 0, "total_tokens": 100},
                })
                self.assertEqual(body["root_tokens"]["total_tokens"], 100)
                self.assertIsNone(body["worker_tokens"])

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


if __name__ == "__main__":
    unittest.main()
