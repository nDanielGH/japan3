#!/usr/bin/env python3
"""Validate the repository invariants used by planning agents.

This intentionally uses only the Python standard library so it can run in a
fresh checkout: python scripts/validate.py
"""

from __future__ import annotations

import ast
import argparse
import re
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRIAGE = {"inbox", "shortlisted", "selected", "skipped"}
IGNORED_PATH_PARTS = {".git", ".cursor", ".firecrawl"}
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SOURCE_LINE = re.compile(
    r"^\s*-\s+.+\s+—\s+\[[^\]]+\]\(https?://[^)]+\)\s+—\s+accessed\s+\d{4}-\d{2}-\d{2}\s*$"
)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
SELECTED_LINK = re.compile(
    r"^\.\./attractions/selected/[a-z0-9]+(?:-[a-z0-9]+)*\.md$"
)
STABLE_REF = re.compile(
    r"(?<![\w/])([a-z0-9]+(?:-[a-z0-9]+)*)/([a-z0-9]+(?:-[a-z0-9]+)*)(?![\w/])"
)
SOURCE_DATE = re.compile(r"accessed\s+(\d{4}-\d{2}-\d{2})\s*$", re.I)
SUNSET_TIME = re.compile(r"(?:[01]\d|2[0-3]):[0-5]\d")
SUNSET_RANGE = re.compile(
    r"^\s*(\d{4}-\d{2}-\d{2})(?:\s+to\s+(\d{4}-\d{2}-\d{2}))?\s*$"
)

HUB_FIELDS = {
    "schema_version",
    "id",
    "name",
    "nights",
    "date_range",
    "base_location",
    "status",
    "notes",
}
HUB_REQUIRED = HUB_FIELDS
ATTRACTION_FIELDS = {
    "schema_version",
    "id",
    "name",
    "priority",
    "area",
    "daylight_sensitive",
    "duration_estimate",
    "booking_required",
    "book_by",
    "skip_reason",
    "sources",
    "notes",
}
ATTRACTION_REQUIRED = ATTRACTION_FIELDS
RESEARCH_FIELDS = {"schema_version", "id", "topic"}
RESEARCH_REQUIRED = RESEARCH_FIELDS
ITINERARY_FIELDS = {"schema_version", "date", "hub", "sunset"}
ITINERARY_REQUIRED = ITINERARY_FIELDS


class Validator:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, path: Path, message: str) -> None:
        self.errors.append(f"{path.relative_to(ROOT)}: {message}")

    def warning(self, path: Path, message: str) -> None:
        self.warnings.append(f"{path.relative_to(ROOT)}: {message}")

    def run(self) -> int:
        root_status = self.check_root()
        self.check_declared_skills()
        trip = self.check_trip_constraints()
        hubs = self.active_hubs(root_status)
        attraction_ids = self.check_hubs(hubs, root_status, trip)
        self.check_links()
        self.check_legacy_assumptions()
        self.check_stable_references(attraction_ids, hubs)

        for warning in self.warnings:
            print(f"WARNING {warning}")
        for error in self.errors:
            print(f"ERROR {error}")
        if self.errors:
            print(f"Validation failed: {len(self.errors)} error(s).")
            return 1
        print("Validation passed.")
        return 0

    def check_declared_skills(self) -> None:
        path = ROOT / "AGENTS.md"
        if not path.exists():
            return
        text = path.read_text(encoding="utf-8")
        section = re.search(
            r"Project skills.*?:\s*\n(.*?)\n\nRead the relevant skill",
            text,
            re.S,
        )
        if not section:
            return
        for skill in re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)*)`", section.group(1)):
            skill_path = ROOT / ".cursor" / "skills" / skill / "SKILL.md"
            if not skill_path.exists():
                self.error(path, f"declared skill is missing: {skill_path.relative_to(ROOT)}")

    def check_root(self) -> dict:
        path = ROOT / "README.md"
        text = path.read_text(encoding="utf-8")
        match = re.search(r"## Status\s+```yaml\s*(.*?)```", text, re.S)
        if not match:
            self.error(path, "missing YAML Status block")
            return {}
        status = parse_yaml_block(match.group(1), self, path)
        if not status.get("focus"):
            self.error(path, "focus must be non-empty")
        if not isinstance(status.get("hubs"), list):
            self.error(path, "hubs must be a YAML list")
        if not status.get("next_actions"):
            self.error(path, "next_actions must be non-empty")
        if not ISO_DATE.match(str(status.get("updated", ""))):
            self.error(path, "updated must be an ISO date")
        elif parse_iso_date(status["updated"]) is None:
            self.error(path, "updated must be a valid calendar date")
        return status

    def check_trip_constraints(self) -> dict:
        path = ROOT / "constraints.md"
        frontmatter, _ = read_frontmatter(path, self)
        values = {}
        for key in ("trip_start", "trip_end"):
            value = frontmatter.get(key)
            if not ISO_DATE.match(str(value)):
                self.error(path, f"{key} must be an ISO date")
            else:
                parsed = parse_iso_date(value)
                if parsed is None:
                    self.error(path, f"{key} must be a valid calendar date")
                else:
                    values[key] = parsed
        nights = frontmatter.get("trip_nights")
        if not isinstance(nights, int) or isinstance(nights, bool):
            self.error(path, "trip_nights must be a positive integer")
        elif nights <= 0:
            self.error(path, "trip_nights must be a positive integer")
        elif "trip_start" in values and "trip_end" in values:
            if (values["trip_end"] - values["trip_start"]).days != nights:
                self.error(path, "trip_nights must equal trip_end minus trip_start")
        return values | {"trip_nights": nights}

    def active_hubs(self, status: dict) -> list[Path]:
        hubs_dir = ROOT / "hubs"
        actual = sorted(
            p for p in hubs_dir.iterdir()
            if p.is_dir() and p.name not in {"_template", "graveyard"} and not p.name.startswith(".")
        )
        listed = status.get("hubs", []) if isinstance(status.get("hubs"), list) else []
        listed_names = [name for name in listed if isinstance(name, str)]
        if len(listed_names) != len(listed) or sorted(listed_names) != [p.name for p in actual]:
            self.error(ROOT / "README.md", f"hubs list {listed!r} does not match active folders")
        for hub in actual:
            if not KEBAB.match(hub.name):
                self.error(hub, "active hub folder must be kebab-case")
        return actual

    def check_hubs(self, hubs: list[Path], status: dict, trip: dict) -> dict[str, set[str]]:
        all_attractions: dict[str, set[str]] = {}
        ranges: list[tuple[date, date, Path]] = []
        scheduled_hubs = 0
        for hub in hubs:
            required = {"README.md", "constraints.md", "attractions", "itinerary", "research"}
            for name in required:
                if not (hub / name).exists():
                    self.error(hub, f"missing required path {name}")
            readme = hub / "README.md"
            meta, _ = read_frontmatter(readme, self)
            self.check_metadata(readme, meta, HUB_FIELDS, HUB_REQUIRED)
            if meta.get("id") != hub.name:
                self.error(readme, "id must match the hub folder name")
            if meta.get("status") not in {"candidate", "active", "complete"}:
                self.error(readme, "status must be candidate, active, or complete")
            if not isinstance(meta.get("name"), str) or not meta.get("name").strip():
                self.error(readme, "name must be a non-empty string")
            if meta.get("nights") is not None and (
                not isinstance(meta.get("nights"), int)
                or isinstance(meta.get("nights"), bool)
            ):
                self.error(readme, "nights must be an integer or null")

            hub_ids: set[str] = set()
            attractions = hub / "attractions"
            if attractions.exists():
                for child in attractions.iterdir():
                    if child.is_dir() and child.name not in TRIAGE:
                        self.error(child, "unknown attraction collection")
                    elif child.is_file() and child.name != "_template.md":
                        self.error(child, "unexpected file directly under attractions/")
            for folder in sorted(TRIAGE):
                directory = attractions / folder
                if not directory.exists():
                    self.error(attractions, f"missing triage folder {folder}")
                    continue
                for path in directory.glob("*.md"):
                    if path.name == "_template.md":
                        continue
                    metadata, body = read_frontmatter(path, self)
                    self.check_metadata(path, metadata, ATTRACTION_FIELDS, ATTRACTION_REQUIRED)
                    self.check_id(path, metadata, path.stem, hub_ids)
                    self.check_attraction_types(path, metadata)
                    if folder == "skipped" and not metadata.get("skip_reason"):
                        self.error(path, "skipped attraction needs skip_reason")
                    if folder != "skipped" and metadata.get("skip_reason") is not None:
                        self.error(path, "skip_reason must be null outside skipped")
                    self.check_questions(path, body)
            all_attractions[hub.name] = hub_ids
            sunset_ranges = self.check_hub_constraints(hub / "constraints.md")

            research = hub / "research"
            research_ids: set[str] = set()
            for path in research.glob("*.md"):
                if path.name == "_note-template.md":
                    continue
                metadata, body = read_frontmatter(path, self)
                self.check_metadata(path, metadata, RESEARCH_FIELDS, RESEARCH_REQUIRED)
                self.check_id(path, metadata, path.stem, research_ids)
                if not isinstance(metadata.get("topic"), str) or not metadata.get("topic").strip():
                    self.error(path, "topic must be a non-empty string")
                self.check_source_lines(path, body)
                self.check_questions(path, body)

            itinerary_dates: set[date] = set()
            for path in (hub / "itinerary").glob("*.md"):
                if path.name == "_day-template.md":
                    continue
                metadata, body = read_frontmatter(path, self)
                filename_date = path.stem
                if not ISO_DATE.match(filename_date):
                    self.error(path, "itinerary filename must be YYYY-MM-DD.md")
                    continue
                day = parse_iso_date(filename_date)
                if day is None:
                    self.error(path, "itinerary filename must contain a valid calendar date")
                    continue
                if metadata.get("date") != filename_date:
                    self.error(path, "frontmatter date must match filename")
                if metadata.get("hub") != hub.name:
                    self.error(path, "frontmatter hub must match parent hub")
                self.check_metadata(path, metadata, ITINERARY_FIELDS, ITINERARY_REQUIRED)
                if day in itinerary_dates:
                    self.error(path, "duplicate itinerary date")
                itinerary_dates.add(day)
                self.check_selected_links(path, body, hub)
                sunset = metadata.get("sunset")
                if sunset is None:
                    self.error(path, "itinerary sunset must be sourced local HH:MM data")
                elif not isinstance(sunset, str) or not SUNSET_TIME.fullmatch(sunset):
                    self.error(path, "itinerary sunset must be a local HH:MM value")
                else:
                    matching_sunsets = [
                        value for start, end, value, _ in sunset_ranges if start <= day <= end
                    ]
                    if not matching_sunsets:
                        self.error(path, "itinerary sunset date is missing from hub constraints")
                    elif sunset not in matching_sunsets:
                        self.error(path, "itinerary sunset does not match hub constraints")

            nights = meta.get("nights")
            date_range = parse_date_range(meta.get("date_range"))
            has_nights = nights is not None
            has_date_range = meta.get("date_range") is not None
            if has_nights != has_date_range:
                self.error(readme, "nights and date_range must be provided together")
            if has_nights and (
                not isinstance(nights, int) or isinstance(nights, bool) or nights <= 0
            ):
                self.error(readme, "scheduled hubs need positive integer nights")
            if has_date_range and date_range is None:
                self.error(readme, "date_range must be [start, end] with ISO dates")
            if date_range:
                start, end = date_range
                trip_start = trip.get("trip_start")
                trip_end = trip.get("trip_end")
                if (
                    not isinstance(trip_start, date)
                    or not isinstance(trip_end, date)
                    or not (trip_start <= start <= end <= trip_end)
                ):
                    self.error(readme, "date_range must be inside the canonical trip window")
                if isinstance(nights, int) and (end - start).days != nights:
                    self.error(readme, "nights must equal date_range end minus start")
                ranges.append((start, end, readme))
                scheduled_hubs += 1
                for day in itinerary_dates:
                    if not (start <= day < end):
                        self.error(hub / "itinerary", f"itinerary date outside sleep range: {day}")
                if meta.get("status") == "complete":
                    expected = {
                        start.fromordinal(start.toordinal() + offset)
                        for offset in range((end - start).days)
                    }
                    missing = sorted(expected - itinerary_dates)
                    if missing:
                        self.error(
                            hub / "itinerary",
                            f"complete hub is missing itinerary days: {', '.join(map(str, missing))}",
                        )
            elif itinerary_dates:
                self.error(readme, "itinerary days require a valid hub schedule")

        if ranges:
            ranges.sort()
            for previous, current in zip(ranges, ranges[1:]):
                if previous[1] > current[0]:
                    self.error(current[2], "hub date ranges must not overlap")
            if scheduled_hubs == len(hubs):
                if ranges[0][0] != trip.get("trip_start") or ranges[-1][1] != trip.get("trip_end"):
                    self.error(ROOT / "constraints.md", "hub date ranges must cover the trip window")
                for previous, current in zip(ranges, ranges[1:]):
                    if previous[1] != current[0]:
                        self.error(current[2], "hub date ranges must be contiguous with no gap or overlap")
                total = sum((end - start).days for start, end, _ in ranges)
                if total != trip.get("trip_nights"):
                    self.error(ROOT / "constraints.md", "hub nights must sum to trip_nights")
        return all_attractions

    def check_id(self, path: Path, metadata: dict, expected: str, seen: set[str]) -> None:
        identifier = metadata.get("id")
        if identifier != expected:
            self.error(path, f"id must match filename stem {expected!r}")
        if not isinstance(identifier, str) or not KEBAB.match(identifier):
            self.error(path, "id must be lowercase kebab-case")
        if identifier in seen:
            self.error(path, f"duplicate id {identifier!r}")
        seen.add(identifier)

    def check_metadata(
        self,
        path: Path,
        metadata: dict,
        allowed: set[str],
        required: set[str],
    ) -> None:
        if metadata.get("schema_version") != 1:
            self.error(path, "schema_version must be 1")
        missing = sorted(required - set(metadata))
        if missing:
            self.error(path, f"missing frontmatter field(s): {', '.join(missing)}")
        unknown = sorted(set(metadata) - allowed)
        if unknown:
            self.error(path, f"unknown frontmatter field(s): {', '.join(unknown)}")

    def check_attraction_types(self, path: Path, metadata: dict) -> None:
        if not isinstance(metadata.get("name"), str) or not metadata.get("name").strip():
            self.error(path, "name must be a non-empty string")
        for field in ("name", "priority", "area", "duration_estimate", "book_by", "skip_reason", "notes"):
            value = metadata.get(field)
            if value is not None and not isinstance(value, str):
                self.error(path, f"{field} must be a string or null")
        for field in ("daylight_sensitive", "booking_required"):
            value = metadata.get(field)
            if value is not None and not isinstance(value, bool):
                self.error(path, f"{field} must be yes, no, or null")
        if not isinstance(metadata.get("sources"), list):
            self.error(path, "sources must be a list")

    def check_hub_constraints(self, path: Path) -> list[tuple[date, date, str, str]]:
        if not path.exists():
            return []
        body = path.read_text(encoding="utf-8")
        in_daylight = False
        ranges: list[tuple[date, date, str, str]] = []
        for line in body.splitlines():
            if re.match(r"^##+\s+Daylight\s*$", line, re.I):
                in_daylight = True
                continue
            if in_daylight and re.match(r"^##+\s+", line):
                in_daylight = False
            if not in_daylight or not line.strip().startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 3 or cells[0].lower() == "date range":
                continue
            if not cells[0] or set(cells[0]) <= {"-", " "}:
                continue
            match = SUNSET_RANGE.fullmatch(cells[0])
            if not match:
                self.error(
                    path,
                    "sunset table date range must use YYYY-MM-DD or "
                    "YYYY-MM-DD to YYYY-MM-DD",
                )
                continue
            start = parse_iso_date(match.group(1))
            end = parse_iso_date(match.group(2) or match.group(1))
            if start is None or end is None or end < start:
                self.error(path, "sunset table contains an invalid calendar date range")
                continue
            if not SUNSET_TIME.fullmatch(cells[1]):
                self.error(path, "sunset table must contain a local HH:MM value")
            source_match = re.search(r"https?://\S+", cells[2])
            accessed_match = SOURCE_DATE.search(cells[2])
            if (
                not source_match
                or not accessed_match
                or parse_iso_date(accessed_match.group(1)) is None
            ):
                self.error(
                    path,
                    "sunset table source must include a URL and accessed YYYY-MM-DD",
                )
            ranges.append((start, end, cells[1], cells[2]))
        ordered = sorted(ranges)
        for previous, current in zip(ordered, ordered[1:]):
            if previous[1] >= current[0]:
                self.error(path, "sunset table date ranges must not overlap")
        return ranges

    def check_source_lines(self, path: Path, body: str) -> None:
        in_sources = False
        for line in body.splitlines():
            if re.match(r"^##+\s+Sources\s*$", line, re.I):
                in_sources = True
                continue
            if in_sources and re.match(r"^##+\s+", line):
                in_sources = False
            if in_sources and line.strip().startswith("- ") and not line.strip().startswith("<!--"):
                if not SOURCE_LINE.match(line):
                    self.error(path, "source line must include title, URL, and accessed YYYY-MM-DD")
                else:
                    source_date = SOURCE_DATE.search(line)
                    if source_date and parse_iso_date(source_date.group(1)) is None:
                        self.error(path, "source accessed date must be a valid calendar date")

    def check_questions(self, path: Path, body: str) -> None:
        if "UNVERIFIED" not in body:
            return
        in_questions = False
        questions = []
        for line in body.splitlines():
            if re.match(r"^##+\s+Open questions\s*$", line, re.I):
                in_questions = True
                continue
            if in_questions and re.match(r"^##+\s+", line):
                in_questions = False
            if in_questions and line.strip().startswith("- [ ]"):
                questions.append(line[5:].strip().lower())
        if not questions:
            self.error(path, "UNVERIFIED claim needs an unchecked Open questions item")
            return
        claims = [
            line.lower()
            for line in body.splitlines()
            if "UNVERIFIED" in line and not line.strip().startswith("- [ ]")
        ]
        for claim in claims:
            words = {word for word in re.findall(r"[a-z0-9]{4,}", claim) if word != "unverified"}
            minimum = 2 if len(words) >= 2 else 1
            if not any(
                len(words & set(re.findall(r"[a-z0-9]{4,}", question))) >= minimum
                for question in questions
            ):
                self.error(path, "UNVERIFIED claim lacks a matching open question")

    def check_links(self) -> None:
        for path in ROOT.rglob("*.md"):
            if any(part in IGNORED_PATH_PARTS for part in path.parts):
                continue
            text = path.read_text(encoding="utf-8")
            for target in MARKDOWN_LINK.findall(text):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                target_path = target.split("#", 1)[0]
                if not target_path or target_path in {"URL", "url"} or target_path.endswith("/slug.md"):
                    continue
                resolved = (path.parent / target_path).resolve()
                if not resolved.exists():
                    self.error(path, f"broken Markdown link {target}")

    def check_legacy_assumptions(self) -> None:
        for path in ROOT.rglob("*.md"):
            if any(part in IGNORED_PATH_PARTS for part in path.parts):
                continue
            text = path.read_text(encoding="utf-8")
            if "(assumed " in text:
                self.error(path, "legacy '(assumed ...)' marker is not allowed")

    def check_selected_links(self, path: Path, body: str, hub: Path) -> None:
        for target in MARKDOWN_LINK.findall(body):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            if not SELECTED_LINK.fullmatch(target):
                self.error(path, "itinerary links must use ../attractions/selected/<slug>.md")
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                self.error(path, f"broken link {target}")
            elif "attractions" in Path(target).parts and "selected" not in Path(target).parts:
                self.error(path, "itinerary attraction links must target selected/")
            elif "attractions" in Path(target).parts and resolved.parent != hub / "attractions" / "selected":
                self.error(path, "itinerary attraction link points outside this hub")

    def check_stable_references(self, attraction_ids: dict[str, set[str]], hubs: list[Path]) -> None:
        for hub in hubs:
            for directory in ((hub / "research"), (hub / "attractions")):
                for path in directory.rglob("*.md"):
                    if path.name.startswith("_"):
                        continue
                    text = path.read_text(encoding="utf-8")
                    for ref_hub, slug in STABLE_REF.findall(text):
                        if ref_hub in {"hubs", "attractions", "research", "itinerary"}:
                            continue
                        known_hubs = set(attraction_ids) | {
                            path.name
                            for path in (
                                (ROOT / "hubs" / "graveyard").iterdir()
                                if (ROOT / "hubs" / "graveyard").exists()
                                else []
                            )
                            if path.is_dir()
                        }
                        if ref_hub not in known_hubs:
                            self.error(path, f"unknown stable attraction reference {ref_hub}/{slug}")
                        elif ref_hub in attraction_ids and slug not in attraction_ids[ref_hub]:
                            self.error(path, f"unknown stable attraction reference {ref_hub}/{slug}")


def parse_yaml_block(text: str, validator: Validator, path: Path) -> dict:
    result: dict = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            if line and not line.startswith("#"):
                validator.error(path, "malformed YAML frontmatter line")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if not key:
            validator.error(path, "frontmatter key must not be empty")
            continue
        if key in result:
            validator.error(path, f"duplicate frontmatter field {key!r}")
            continue
        result[key] = parse_scalar(value.strip())
    return result


def parse_scalar(value: str):
    value = value.split(" #", 1)[0].strip()
    if value in {"null", "~", ""}:
        return None
    if value.lower() in {"yes", "true"}:
        return True
    if value.lower() in {"no", "false"}:
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [] if not inner else [parse_scalar(item.strip()) for item in inner.split(",")]
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value[1:-1]
    return value


def read_frontmatter(path: Path, validator: Validator) -> tuple[dict, str]:
    if not path.exists():
        return {}, ""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        validator.error(path, "missing YAML frontmatter")
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        validator.error(path, "unterminated YAML frontmatter")
        return {}, text
    return parse_yaml_block(text[4:end], validator, path), text[end + 4:]


def parse_date_range(value) -> tuple[date, date] | None:
    if not isinstance(value, list) or len(value) != 2:
        return None
    if not all(isinstance(item, str) and ISO_DATE.match(item) for item in value):
        return None
    start = parse_iso_date(value[0])
    end = parse_iso_date(value[1])
    if start is None or end is None:
        return None
    return (start, end) if start <= end else None


def parse_iso_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def find_references(target: str) -> list[tuple[Path, int, str]]:
    """Return Markdown lines that mention a target file."""
    target_path = (ROOT / target).resolve()
    if not target_path.exists() or target_path.suffix.lower() != ".md":
        raise ValueError(f"target must be an existing Markdown file: {target}")
    relative_name = target_path.relative_to(ROOT).as_posix()
    names = {target_path.name, relative_name}
    references = []
    for path in ROOT.rglob("*.md"):
        if path.resolve() == target_path or any(part in IGNORED_PATH_PARTS for part in path.parts):
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if any(name in line for name in names):
                references.append((path, line_number, line.strip()))
    return references


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--references",
        metavar="FILE",
        help="list Markdown files and lines that mention FILE, then exit",
    )
    parser.add_argument(
        "--root",
        metavar="DIRECTORY",
        help="validate a repository snapshot rooted at DIRECTORY",
    )
    args = parser.parse_args()
    if args.root:
        ROOT = Path(args.root).resolve()
    if args.references:
        try:
            references = find_references(args.references)
        except ValueError as error:
            parser.error(str(error))
        for path, line_number, line in references:
            print(f"{path.relative_to(ROOT)}:{line_number}: {line}")
        print(f"{len(references)} inbound Markdown reference(s).")
        sys.exit(0)
    sys.exit(Validator().run())
