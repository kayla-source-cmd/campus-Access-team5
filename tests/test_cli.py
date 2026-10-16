import io
import os
import tempfile
import unittest
from unittest.mock import patch

from campus_access import cli, storage


class CliTests(unittest.TestCase):
    def setUp(self):
        storage.reset_requests()
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "requests.json")

    def tearDown(self):
        self.tmp.cleanup()

    def run_with(self, inputs):
        out = io.StringIO()
        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", out):
            cli.run_menu(self.path)
        return out.getvalue()

    def test_invalid_menu_option_shows_message_and_allows_retry(self):
        output = self.run_with(["x", "99", "9", "n"])
        self.assertIn("Invalid option 'x'", output)
        self.assertIn("Invalid option '99'", output)
        self.assertIn("Goodbye", output)

    def test_bad_card_type_shows_error_and_creates_nothing(self):
        output = self.run_with(["1", "F001", "alien", "9", "n"])
        self.assertIn("Invalid card type", output)
        self.assertEqual(storage.list_requests(), [])

    def test_full_workflow_through_menu(self):
        self.run_with([
            "1", "F001", "visitor",
            "3", "A001", "M01",
            "4", "A001",
            "5", "A001",
            "9", "n",
        ])
        self.assertEqual(storage.get_request("A001")["status"], "returned")

    def test_corrupt_file_stops_startup_and_is_not_overwritten(self):
        with open(self.path, "w") as file:
            file.write("{ not json")
        output = self.run_with([])
        self.assertIn("Cannot start", output)
        with open(self.path) as file:
            self.assertEqual(file.read(), "{ not json")


if __name__ == "__main__":
    unittest.main() 