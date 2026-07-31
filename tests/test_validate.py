import contextlib
import io
import unittest
from datetime import date

from scripts.validate import Validator, find_references, parse_date_range, parse_scalar


class ValidatorHelpersTest(unittest.TestCase):
    def test_parse_scalar_supports_schema_values(self):
        self.assertEqual(parse_scalar("null"), None)
        self.assertEqual(parse_scalar("yes"), True)
        self.assertEqual(parse_scalar("32"), 32)
        self.assertEqual(parse_scalar("[tokyo, kyoto]"), ["tokyo", "kyoto"])

    def test_parse_date_range_requires_two_iso_dates(self):
        self.assertEqual(
            parse_date_range(["2026-10-18", "2026-11-19"]),
            (date(2026, 10, 18), date(2026, 11, 19)),
        )
        self.assertIsNone(parse_date_range(["2026-10-18"]))
        self.assertIsNone(parse_date_range(["2026-11-19", "2026-10-18"]))

    def test_repository_is_valid_at_stage_zero(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = Validator().run()
        self.assertEqual(result, 0, output.getvalue())

    def test_reference_audit_finds_inbound_markdown_mentions(self):
        references = find_references("README.md")
        paths = {path.name for path, _, _ in references}
        self.assertIn("AGENTS.md", paths)


if __name__ == "__main__":
    unittest.main()
