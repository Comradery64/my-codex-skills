import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]


class SkillPolicyTests(unittest.TestCase):
    def test_both_skills_require_absolute_gates_and_no_history(self):
        for name in ("stingy-sol", "austere-astra"):
            with self.subTest(skill=name):
                text = (ROOT / "skills" / name / "SKILL.md").read_text()
                for required in ("token_budget_guard.py", "100,000", "250,000",
                                 "explicit user confirmation", "fork_turns=\"none\""):
                    self.assertIn(required, text)
                self.assertNotIn("Give full history", text)

    def test_stingy_forbids_nested_teams_and_slot_filling(self):
        files = [ROOT / "skills/stingy-sol/SKILL.md",
                 ROOT / "skills/stingy-sol/references/fanout-template.md"]
        text = "\n".join(path.read_text() for path in files)
        self.assertIn("Children never", text)
        self.assertNotIn("available slots", text)
        self.assertNotIn("child create its own team", text)


if __name__ == "__main__":
    unittest.main()
