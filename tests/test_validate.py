import contextlib
import io
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from scripts.validate import Validator, find_references, parse_date_range, parse_scalar


class ValidatorHelpersTest(unittest.TestCase):
    def make_partial_repository(self, root: Path):
        (root / "hubs").mkdir()
        (root / "constraints.md").write_text(
            "---\ntrip_start: 2026-10-18\ntrip_end: 2026-11-19\ntrip_nights: 32\n---\n",
            encoding="utf-8",
        )
        (root / "README.md").write_text(
            "## Status\n\n```yaml\n"
            "focus: research\nhubs: [tokyo, osaka]\n"
            "next_actions: research tokyo; schedule osaka\nupdated: 2026-08-01\n"
            "```\n",
            encoding="utf-8",
        )
        for hub, schedule in (
            ("tokyo", "nights: 5\ndate_range: [2026-10-18, 2026-10-23]"),
            ("osaka", "nights: null\ndate_range: null"),
        ):
            hub_root = root / "hubs" / hub
            for directory in ("attractions/inbox", "attractions/shortlisted",
                              "attractions/selected", "attractions/skipped",
                              "itinerary", "research"):
                (hub_root / directory).mkdir(parents=True)
            (hub_root / "README.md").write_text(
                f"---\nschema_version: 1\nid: {hub}\nname: {hub.title()}\n{schedule}\n"
                "base_location: null\nstatus: candidate\nnotes: null\n---\n",
                encoding="utf-8",
            )
            (hub_root / "constraints.md").write_text("# Constraints\n", encoding="utf-8")

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
        self.assertIsNone(parse_date_range(["2026-99-99", "2026-10-18"]))

    def test_repository_is_valid_with_iterative_dashboard(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = Validator().run()
        self.assertEqual(result, 0, output.getvalue())

    def test_hubs_can_progress_independently(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_partial_repository(root)
            with patch("scripts.validate.ROOT", root):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    result = Validator().run()
            self.assertEqual(result, 0, output.getvalue())

    def test_reference_audit_finds_inbound_markdown_mentions(self):
        references = find_references("README.md")
        paths = {path.name for path, _, _ in references}
        self.assertIn("AGENTS.md", paths)

    def test_complete_hub_requires_every_scheduled_day(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_partial_repository(root)
            hub_root = root / "hubs" / "tokyo"
            readme = hub_root / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8").replace(
                    "status: candidate", "status: complete"
                ),
                encoding="utf-8",
            )
            (hub_root / "constraints.md").write_text(
                "# Constraints\n\n## Daylight\n\n"
                "| Date range | Sunset (local) | Source / accessed |\n"
                "| ---------- | -------------- | ----------------- |\n"
                "| 2026-10-18 to 2026-10-22 | 16:58 | "
                "https://example.com/almanac — accessed 2026-08-01 |\n",
                encoding="utf-8",
            )
            (hub_root / "itinerary" / "2026-10-18.md").write_text(
                "---\nschema_version: 1\ndate: 2026-10-18\nhub: tokyo\n"
                'sunset: "16:58"\n---\n# Day\n',
                encoding="utf-8",
            )
            with patch("scripts.validate.ROOT", root):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    result = Validator().run()
            self.assertEqual(result, 1, output.getvalue())
            self.assertIn("missing itinerary days", output.getvalue())

    def test_itinerary_rejects_non_selected_local_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_partial_repository(root)
            hub_root = root / "hubs" / "tokyo"
            (hub_root / "constraints.md").write_text(
                "# Constraints\n\n## Daylight\n\n"
                "| Date range | Sunset (local) | Source / accessed |\n"
                "| ---------- | -------------- | ----------------- |\n"
                "| 2026-10-18 | 16:58 | "
                "https://example.com/almanac — accessed 2026-08-01 |\n",
                encoding="utf-8",
            )
            (hub_root / "itinerary" / "2026-10-18.md").write_text(
                "---\nschema_version: 1\ndate: 2026-10-18\nhub: tokyo\n"
                'sunset: "16:58"\n---\n# Day\n[Hub](../README.md)\n',
                encoding="utf-8",
            )
            with patch("scripts.validate.ROOT", root):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    result = Validator().run()
            self.assertEqual(result, 1, output.getvalue())
            self.assertIn("itinerary links must use", output.getvalue())

    def test_unknown_attraction_collection_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_partial_repository(root)
            unknown = root / "hubs" / "tokyo" / "attractions" / "other"
            unknown.mkdir()
            (unknown / "idea.md").write_text("unvalidated", encoding="utf-8")
            with patch("scripts.validate.ROOT", root):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    result = Validator().run()
            self.assertEqual(result, 1, output.getvalue())
            self.assertIn("unknown attraction collection", output.getvalue())

    def test_required_frontmatter_is_enforced(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_partial_repository(root)
            readme = root / "hubs" / "tokyo" / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8").replace("notes: null\n", ""),
                encoding="utf-8",
            )
            with patch("scripts.validate.ROOT", root):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    result = Validator().run()
            self.assertEqual(result, 1, output.getvalue())
            self.assertIn("missing frontmatter field(s): notes", output.getvalue())


if __name__ == "__main__":
    unittest.main()
