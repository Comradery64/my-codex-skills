import unittest
import unittest.mock
from pathlib import Path

ROOT = Path(__file__).parents[1]


class SkillPolicyTests(unittest.TestCase):
    SKILLS = ("stingy-sol", "austere-astra")
    SHARED = ("model-catalog.md", "orchestration.md", "cost-model.md",
              "verification-contracts.md")
    SCRIPTS = ("token_budget_guard.py", "receipt_check.py")

    def skill(self, name):
        return (ROOT / "skills" / name / "SKILL.md").read_text()

    def reference(self, name):
        return (ROOT / "skills" / "austere-astra" / "references" / name).read_text()

    def test_both_skills_require_budget_telemetry_and_no_history(self):
        for name in self.SKILLS:
            with self.subTest(skill=name):
                normalized = " ".join(self.skill(name).split())
                for required in ("token_budget_guard.py", "100,000", "250,000",
                                 "fork_turns=\"none\""):
                    self.assertIn(required, normalized)
                for reference in self.SHARED:
                    self.assertIn(f"references/{reference}", self.skill(name))

    def test_shared_references_are_identical(self):
        for reference in self.SHARED:
            with self.subTest(reference=reference):
                copies = [(ROOT / "skills" / name / "references" / reference).read_bytes()
                          for name in self.SKILLS]
                self.assertEqual(copies[0], copies[1])

    def test_shared_scripts_are_identical(self):
        for script in self.SCRIPTS:
            with self.subTest(script=script):
                copies = [(ROOT / "skills" / name / "scripts" / script).read_bytes()
                          for name in self.SKILLS]
                self.assertEqual(copies[0], copies[1])

    def test_root_owns_dynamic_topology(self):
        for name in self.SKILLS:
            with self.subTest(skill=name):
                orchestration = (ROOT / "skills" / name / "references" /
                                 "orchestration.md").read_text()
                combined = self.skill(name) + orchestration
                self.assertIn("never delegate to other workers", self.skill(name))
                self.assertIn("parallel", combined.lower())
                self.assertIn("waterfall", combined.lower())
                self.assertIn("After every return", combined)
                self.assertNotIn("child may spawn", combined.lower())

    def test_model_roles_are_categorized(self):
        catalog = self.reference("model-catalog.md")
        for model in ("gpt-6-astra", "gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna"):
            self.assertIn(model, catalog)
        self.assertIn("Semantic codebase tracing", catalog)
        self.assertIn("Enumeration, extraction", catalog)

    # --- mitigations from the 2026-09-08 incident ------------------------------

    def test_objective_is_all_role_total_not_root_share(self):
        """M01: root share is a diagnostic, never evidence of savings."""
        for text in [self.skill(name) for name in self.SKILLS] + [
                self.reference("cost-model.md")]:
            normalized = " ".join(text.split())
            self.assertIn("total resources consumed to deliver an accepted milestone",
                          normalized)
            self.assertIn("never evidence of savings", normalized)

    def test_checkpoints_produce_action_states(self):
        """M02: every threshold result is an instruction, not a number."""
        states = ("proceed", "reduce or reframe", "bounded diagnostic",
                  "resource blocked", "aggregate usage unavailable")
        for name in self.SKILLS:
            with self.subTest(skill=name):
                normalized = " ".join(self.skill(name).split()).lower()
                for state in states:
                    self.assertIn(state, normalized)
                self.assertIn("exit `40`", self.skill(name))
                self.assertIn("never reset or resize the allowance",
                              " ".join(self.skill(name).split()).lower())

    def test_assignments_are_bounded_by_consumption(self):
        """M03: subject bounds are not consumption bounds."""
        orchestration = " ".join(self.reference("orchestration.md").split())
        for field in ("finite allowance", "early-return condition",
                      "integration reserve", "Return threshold", "No expansion"):
            self.assertIn(field, orchestration)
        self.assertIn("subject bound is not a consumption bound",
                      " ".join(self.skill("austere-astra").split()))

    def test_model_and_effort_are_chosen_separately(self):
        """M04: high effort needs a task-specific reason and is never inherited."""
        catalog = " ".join(self.reference("model-catalog.md").split())
        self.assertIn("Choose model and effort separately", catalog)
        self.assertIn("High effort is never inherited", catalog)
        self.assertIn("spawning no new agent at all", catalog)

    def test_preflight_and_coverage_manifest_are_required(self):
        """M05 and M06: cheap integration checks and a coverage denominator."""
        contracts = " ".join(self.reference("verification-contracts.md").split())
        self.assertIn("Preflight before any long test", contracts)
        self.assertIn("A failing preflight cancels the scheduled expensive stage",
                      contracts)
        for field in ("population", "expected", "observed", "missing", "duplicate",
                      "coalesced", "final_gap_ms"):
            self.assertIn(field, contracts)
        self.assertIn("not a pass", contracts)

    def test_receipts_must_be_complete_before_acceptance(self):
        """M07: a receipt omitting a criterion ID is incomplete, not a pass."""
        orchestration = " ".join(self.reference("orchestration.md").split())
        self.assertIn("receipt_check.py", orchestration)
        self.assertIn("is incomplete, not a phase pass", orchestration)
        for name in self.SKILLS:
            with self.subTest(skill=name):
                self.assertIn("incomplete, not a phase pass",
                              " ".join(self.skill(name).split()))

    def test_invariant_examples_precede_implementation(self):
        """M08: consequential invariants get failure examples up front."""
        contracts = " ".join(self.reference("verification-contracts.md").split())
        self.assertIn("Invariant failure examples before implementation", contracts)
        self.assertIn("resolve that architecture question first", contracts)

    def test_context_reuse_requires_retirement(self):
        """M09: reuse is a cost decision judged over the whole history."""
        for text in (self.reference("orchestration.md"), self.reference("cost-model.md")):
            normalized = " ".join(text.split())
            self.assertIn("entire history", normalized)
            self.assertIn("cheaper than a concise fresh", normalized)

    def test_guardian_overhead_is_accounted(self):
        """M10: guardians are a separate role inside the same total."""
        cost = " ".join(self.reference("cost-model.md").split())
        self.assertIn("automatic guardians", cost)
        self.assertIn("Folding them into worker totals hides real overhead", cost)
        for name in self.SKILLS:
            with self.subTest(skill=name):
                self.assertIn("guardian", self.skill(name).lower())

    def test_user_correction_changes_the_next_dispatch(self):
        """M11: a correction persists an operating-policy delta."""
        orchestration = " ".join(self.reference("orchestration.md").split())
        self.assertIn("operating-policy delta", orchestration)
        self.assertIn("preserves that worker", orchestration)
        for name in self.SKILLS:
            with self.subTest(skill=name):
                normalized = " ".join(self.skill(name).split())
                self.assertIn("operating-policy delta", normalized)
                self.assertIn("under unchanged bounds after a correction", normalized)

    def test_unit_and_enforcement_are_declared(self):
        """G01 and G05: a usable unit, and no promised hard cap."""
        cost = " ".join(self.reference("cost-model.md").split())
        for mode in ("runtime", "dispatch_boundary", "cooperative"):
            self.assertIn(mode, cost)
        self.assertIn("there is no hard spending cap", cost)
        self.assertIn("Missing account telemetry is `unknown`", cost)

    def test_milestone_accounting_is_stable_and_contract_is_declared(self):
        """G02 and the section-4 operational contract."""
        cost = " ".join(self.reference("cost-model.md").split())
        self.assertIn("stable milestone ID", cost)
        self.assertIn("replanning never replenishes the allowance", cost)
        raw = self.reference("cost-model.md")
        for key in ("milestone_id:", "enforcement:", "integration_reserve:",
                    "repair_reserve:", "next_assignment_upper:", "return_threshold:",
                    "no_expansion:"):
            self.assertIn(key, raw)
        self.assertIn("A missing allowance is invalid, not unlimited", cost)

    def test_comparative_target_is_out_of_acceptance(self):
        """G03: no invented savings percentage."""
        cost = " ".join(self.reference("cost-model.md").split())
        self.assertIn("never an invented savings percentage", cost)
        astra = " ".join(self.skill("austere-astra").split())
        self.assertIn("stays out of acceptance unless scope, quality, accounting "
                      "classes, and a matched baseline are all available", astra)

    def test_root_review_is_focused_and_phases_close(self):
        """G04 and G07."""
        orchestration = " ".join(self.reference("orchestration.md").split())
        self.assertIn("focuses on the decision that can change acceptance", orchestration)
        self.assertIn("Keep one rolling state artifact", orchestration)
        self.assertIn("does not authorize an economically unbounded", orchestration)

    def test_effective_configuration_is_recorded_not_mutated(self):
        """G06: requested versus effective, recorded once."""
        for name in self.SKILLS:
            with self.subTest(skill=name):
                normalized = " ".join(self.skill(name).split())
                self.assertIn("Record requested and effective values once", normalized)
                self.assertIn("never prescribe raising effort as a cost repair",
                              normalized.lower())


class BehavioralFixtureTests(unittest.TestCase):
    """Every declared case renders for both skills and has a rubric section."""

    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "render_prompt", ROOT / "tests" / "behavioral" / "render_prompt.py")
        self.renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.renderer)

    def test_every_case_has_a_fixture_and_a_rubric_section(self):
        rubric = (ROOT / "tests" / "behavioral" / "rubric.md").read_text().lower()
        for case in self.renderer.CASES:
            with self.subTest(case=case):
                path = ROOT / "tests" / "behavioral" / "cases" / f"{case}.md"
                self.assertTrue(path.exists(), path)
                self.assertIn("## INPUT", path.read_text())
                heading = case.replace("_", " ")
                self.assertIn(f"## {heading}", rubric)

    def test_cases_carry_no_grading_language(self):
        for case in self.renderer.CASES:
            with self.subTest(case=case):
                text = (ROOT / "tests" / "behavioral" / "cases" / f"{case}.md").read_text()
                for leak in ("pass when", "fail if", "expected outcome", "rubric"):
                    self.assertNotIn(leak, text.lower())

    def test_renderer_packet_includes_every_shared_reference(self):
        import io
        import contextlib
        for skill in self.renderer.SKILLS:
            with self.subTest(skill=skill):
                buffer = io.StringIO()
                argv = ["render_prompt.py", "--skill", skill, "--case", self.renderer.CASES[-1]]
                with contextlib.redirect_stdout(buffer), \
                        unittest.mock.patch("sys.argv", argv):
                    self.renderer.main()
                packet = buffer.getvalue()
                self.assertIn(f"skills/{skill}/SKILL.md", packet)
                for reference in SkillPolicyTests.SHARED:
                    self.assertIn(f"skills/{skill}/references/{reference}", packet)
                self.assertIn("sha256=", packet)
                self.assertNotIn("Pass when", packet)


if __name__ == "__main__":
    unittest.main()
