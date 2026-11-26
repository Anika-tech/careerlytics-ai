import unittest
import tempfile
from pathlib import Path
from modules.text_preprocessing import clean_text
from modules.skills_extractor import extract_technical_skills, extract_soft_skills
from modules.skill_gap import calculate_skill_gap
from modules.job_recommender import build_apply_search_url, parse_experience
from modules.auth import authenticate_user, create_user


class ModuleTests(unittest.TestCase):
    def test_clean_text(self):
        self.assertEqual(clean_text("Python   + SQL!"), "python + sql")

    def test_skill_extraction_boundaries(self):
        text = "Experienced in Python, SQL, React and communication."
        self.assertIn("python", extract_technical_skills(text))
        self.assertIn("sql", extract_technical_skills(text))
        self.assertIn("communication", extract_soft_skills(text))
        self.assertNotIn("java", extract_technical_skills("JavaScript developer"))

    def test_skill_gap(self):
        gap = calculate_skill_gap(["python", "sql"], ["python", "docker", "sql"])
        self.assertEqual(gap["matching"], ["python", "sql"])
        self.assertEqual(gap["missing"], ["docker"])

    def test_experience_parser(self):
        self.assertEqual(parse_experience("3-5 years"), (3.0, 5.0))
        self.assertIsNone(parse_experience("Not specified"))

    def test_apply_search_includes_listing_details(self):
        url = build_apply_search_url("Python Developer", "Example Co", "Bengaluru")
        self.assertIn("site%3Anaukri.com", url)
        self.assertIn("Python+Developer", url)
        self.assertIn("Example+Co", url)
        self.assertIn("Bengaluru", url)

    def test_local_account_signup_and_login(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = Path(temp_dir) / "users.sqlite3"
            created, _ = create_user("person@example.com", "long-enough-password", database)
            self.assertTrue(created)
            self.assertTrue(authenticate_user("PERSON@example.com", "long-enough-password", database))
            self.assertFalse(authenticate_user("person@example.com", "wrong-password", database))
            duplicate, _ = create_user("person@example.com", "another-long-password", database)
            self.assertFalse(duplicate)

    def test_signup_rejects_short_password(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            created, message = create_user(
                "person@example.com", "short", Path(temp_dir) / "users.sqlite3"
            )
            self.assertFalse(created)
            self.assertIn("10 characters", message)


if __name__ == "__main__":
    unittest.main()
