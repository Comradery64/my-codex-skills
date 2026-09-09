import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPTS = [ROOT / "skills" / name / "scripts" / "receipt_check.py"
           for name in ("stingy-sol", "austere-astra")]


def receipt(**overrides):
    base = {
        "milestone_id": "p1",
        "claim": "accepted",
        "required_criteria": ["c_reconnect", "c_persistence"],
        "criteria": [
            {"id": "c_reconnect", "status": "pass", "evidence": "artifacts/reconnect.log"},
            {"id": "c_persistence", "status": "pass", "evidence": "artifacts/persist.log"},
        ],
    }
    base.update(overrides)
    return base


class ReceiptCheckTests(unittest.TestCase):
    def run_check(self, script, body, *args):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "receipt.json"
            path.write_text(json.dumps(body))
            result = subprocess.run([sys.executable, str(script), "--receipt", str(path),
                                     "--json", *args], capture_output=True, text=True)
        return result.returncode, json.loads(result.stdout)

    def test_skill_copies_are_identical(self):
        self.assertEqual(SCRIPTS[0].read_bytes(), SCRIPTS[1].read_bytes())

    def test_complete_receipt_passes(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                code, body = self.run_check(script, receipt())
                self.assertEqual(code, 0)
                self.assertEqual(body["status"], "complete")
                self.assertEqual(body["problems"], [])
                self.assertIn("the root still reviews correctness", body["note"])

    def test_omitted_criterion_is_incomplete_not_a_pass(self):
        """M07: the reconnect criterion simply missing from the receipt."""
        for script in SCRIPTS:
            with self.subTest(script=script):
                code, body = self.run_check(script, receipt(criteria=[
                    {"id": "c_persistence", "status": "pass",
                     "evidence": "artifacts/persist.log"}]))
                self.assertEqual(code, 10)
                self.assertEqual(body["status"], "incomplete")
                self.assertTrue(any("c_reconnect" in p for p in body["problems"]))

    def test_pass_without_evidence_is_incomplete(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                code, body = self.run_check(script, receipt(criteria=[
                    {"id": "c_reconnect", "status": "pass"},
                    {"id": "c_persistence", "status": "pass",
                     "evidence": "artifacts/persist.log"}]))
                self.assertEqual(code, 10)
                self.assertTrue(any("no evidence" in p for p in body["problems"]))

    def test_fail_needs_evidence_or_precise_blocker(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                code, _ = self.run_check(script, receipt(claim="partial", criteria=[
                    {"id": "c_reconnect", "status": "fail"},
                    {"id": "c_persistence", "status": "pass",
                     "evidence": "artifacts/persist.log"}]))
                self.assertEqual(code, 10)
                code, body = self.run_check(script, receipt(claim="partial", criteria=[
                    {"id": "c_reconnect", "status": "fail",
                     "blocker": "watcher root not configured; see artifacts/watch.log"},
                    {"id": "c_persistence", "status": "unverified",
                     "blocker": "no fixture for restart"}]))
                self.assertEqual(code, 0)
                self.assertEqual(body["status"], "complete")

    def test_acceptance_claim_with_open_criteria_is_invalid(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                code, body = self.run_check(script, receipt(criteria=[
                    {"id": "c_reconnect", "status": "unverified",
                     "blocker": "never exercised"},
                    {"id": "c_persistence", "status": "pass",
                     "evidence": "artifacts/persist.log"}]))
                self.assertEqual(code, 20)
                self.assertEqual(body["status"], "invalid_claim")
                self.assertTrue(any("c_reconnect" in p for p in body["problems"]))

    def test_required_ids_may_come_from_the_assignment(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                body = receipt()
                del body["required_criteria"]
                code, _ = self.run_check(script, body, "--require",
                                         "c_reconnect,c_persistence,c_replay")
                self.assertEqual(code, 10)
                code, result = self.run_check(script, body)
                self.assertEqual(code, 2)
                self.assertEqual(result["status"], "unusable")

    def test_sparse_latency_sample_cannot_pass(self):
        """M06: ten observations out of six hundred expected advances."""
        for script in SCRIPTS:
            with self.subTest(script=script):
                code, body = self.run_check(script, receipt(coverage={
                    "population": "global_sequence",
                    "sources": ["s1", "s2"],
                    "expected": 600, "observed": 10, "missing": 590,
                    "duplicate": 0, "coalesced": 0, "final_gap_ms": 61000,
                    "latency": {"p95_ms": 1017}}))
                self.assertEqual(code, 20)
                self.assertTrue(any("missing observations" in p for p in body["problems"]))

    def test_coverage_counts_must_reconcile(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                code, body = self.run_check(script, receipt(coverage={
                    "population": "per_session_delivery",
                    "sources": ["s1"], "expected": 600, "observed": 500,
                    "missing": 0, "duplicate": 0, "coalesced": 0,
                    "final_gap_ms": 900}))
                self.assertEqual(code, 20)
                self.assertTrue(any("does not reconcile" in p for p in body["problems"]))

    def test_coverage_needs_population_and_sources(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                code, body = self.run_check(script, receipt(coverage={
                    "expected": 600, "observed": 600, "missing": 0,
                    "duplicate": 0, "coalesced": 0, "final_gap_ms": 900}))
                self.assertEqual(code, 10)
                joined = " ".join(body["problems"])
                self.assertIn("measured population", joined)
                self.assertIn("source event identifiers", joined)

    def test_full_coverage_manifest_passes(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                code, body = self.run_check(script, receipt(coverage={
                    "population": "per_session_delivery",
                    "sources": ["s1", "s2", "s3"],
                    "expected": 600, "observed": 600, "missing": 0,
                    "duplicate": 0, "coalesced": 4, "final_gap_ms": 850,
                    "latency": {"p95_ms": 1017}}))
                self.assertEqual(code, 0)
                self.assertEqual(body["status"], "complete")

    def test_long_test_requires_a_passing_preflight(self):
        """M05: no ten-minute soak before the integration path is proven."""
        for script in SCRIPTS:
            with self.subTest(script=script):
                code, body = self.run_check(script, receipt(long_test=True))
                self.assertEqual(code, 20)
                self.assertTrue(any("no executable preflight" in p
                                    for p in body["problems"]))
                code, body = self.run_check(script, receipt(
                    long_test=True,
                    preflight={"status": "fail", "command": "make preflight",
                               "evidence": "artifacts/preflight.log"}))
                self.assertEqual(code, 20)
                self.assertTrue(any("cancel the expensive stage" in p
                                    for p in body["problems"]))
                code, body = self.run_check(script, receipt(
                    long_test=True,
                    preflight={"status": "pass", "command": "make preflight",
                               "evidence": "artifacts/preflight.log"}))
                self.assertEqual(code, 0)

    def test_unusable_input_is_reported_not_guessed(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                result = subprocess.run(
                    [sys.executable, str(script), "--receipt", "-", "--json",
                     "--require", "c1"], input="not json", capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(json.loads(result.stdout)["status"], "unusable")

    def test_duplicate_criterion_report_is_invalid(self):
        for script in SCRIPTS:
            with self.subTest(script=script):
                code, body = self.run_check(script, receipt(criteria=[
                    {"id": "c_reconnect", "status": "pass", "evidence": "a"},
                    {"id": "c_reconnect", "status": "pass", "evidence": "b"},
                    {"id": "c_persistence", "status": "pass", "evidence": "c"}]))
                self.assertEqual(code, 20)
                self.assertTrue(any("reported twice" in p for p in body["problems"]))


if __name__ == "__main__":
    unittest.main()
