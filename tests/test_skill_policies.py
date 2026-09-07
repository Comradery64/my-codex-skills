import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class SkillPolicyTests(unittest.TestCase):
    SKILLS = ("stingy-sol", "austere-astra")
    SHARED = ("model-catalog.md", "orchestration.md", "cost-model.md")

    def test_both_skills_require_budget_gates_and_no_history(self):
        for name in self.SKILLS:
            with self.subTest(skill=name):
                text = (ROOT / "skills" / name / "SKILL.md").read_text()
                normalized = " ".join(text.split())
                for required in ("token_budget_guard.py", "100,000", "250,000",
                                 "explicit user confirmation", "fork_turns=\"none\""):
                    self.assertIn(required, normalized)
                for reference in self.SHARED:
                    self.assertIn(f"references/{reference}", text)

    def test_shared_references_are_identical(self):
        for reference in self.SHARED:
            with self.subTest(reference=reference):
                copies = [(ROOT / "skills" / name / "references" / reference).read_bytes()
                          for name in self.SKILLS]
                self.assertEqual(copies[0], copies[1])

    def test_root_owns_dynamic_topology(self):
        for name in self.SKILLS:
            with self.subTest(skill=name):
                skill = (ROOT / "skills" / name / "SKILL.md").read_text()
                orchestration = (ROOT / "skills" / name / "references" /
                                 "orchestration.md").read_text()
                combined = skill + orchestration
                self.assertIn("never delegate to other workers", skill)
                self.assertIn("parallel", combined.lower())
                self.assertIn("waterfall", combined.lower())
                self.assertIn("After every return", combined)
                self.assertNotIn("child may spawn", combined.lower())

    def test_model_roles_are_categorized(self):
        catalog = (ROOT / "skills" / "austere-astra" / "references" /
                   "model-catalog.md").read_text()
        for model in ("gpt-6-astra", "gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna"):
            self.assertIn(model, catalog)
        self.assertIn("Semantic codebase tracing", catalog)
        self.assertIn("Enumeration, extraction", catalog)


if __name__ == "__main__":
    unittest.main()
