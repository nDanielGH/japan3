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
KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SOURCE_LINE = re.compile(
    r"^\s*-\s+.+\s+—\s+\[[^\]]+\]\(https?://[^)]+\)\s+—\s+accessed\s+\d{4}-\d{2}-\d{2}\s*$"
)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")
STABLE_REF = re.compile(
    r"(?<![\w/])([a-z0-9]+(?:-[a-z0-9]+)*)/([a-z0-9]+(?:-[a-z0-9]+)*)(?![\w/])"
)


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
                values[key] = date.fromisoformat(value)
        nights = frontmatter.get("trip_nights")
        if not isinstance(nights, int):
            self.error(path, "trip_nights must be an integer")
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
        if sorted(listed) != [p.name for p in actual]:
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
            if meta.get("id") != hub.name:
                self.error(readme, "id must match the hub folder name")
            if meta.get("status") not in {"candidate", "active", "complete"}:
                self.error(readme, "status must be candidate, active, or complete")

            hub_ids: set[str] = set()
            attractions = hub / "attractions"
            for folder in TRIAGE:
                directory = attractions / folder
                if not directory.exists():
                    self.error(attractions, f"missing triage folder {folder}")
                    continue
                for path in directory.glob("*.md"):
                    if path.name == "_template.md":
                        continue
                    metadata, body = read_frontmatter(path, self)
                    self.check_id(path, metadata, path.stem, hub_ids)
                    if folder == "skipped" and not metadata.get("skip_reason"):
                        self.error(path, "skipped attraction needs skip_reason")
                    if folder != "skipped" and metadata.get("skip_reason") is not None:
                        self.error(path, "skip_reason must be null outside skipped")
                    self.check_questions(path, body)
            all_attractions[hub.name] = hub_ids

            research = hub / "research"
            research_ids: set[str] = set()
            for path in research.glob("*.md"):
                if path.name == "_note-template.md":
                    continue
                metadata, body = read_frontmatter(path, self)
                self.check_id(path, metadata, path.stem, research_ids)
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
                day = date.fromisoformat(filename_date)
                if metadata.get("date") != filename_date:
                    self.error(path, "frontmatter date must match filename")
                if metadata.get("hub") != hub.name:
                    self.error(path, "frontmatter hub must match parent hub")
                if day in itinerary_dates:
                    self.error(path, "duplicate itinerary date")
                itinerary_dates.add(day)
                self.check_selected_links(path, body, hub)
                sunset = metadata.get("sunset")
                if sunset is not None and (
                    not isinstance(sunset, str)
                    or not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", sunset)
                ):
                    self.error(path, "itinerary sunset must be a local HH:MM value or null")

            nights = meta.get("nights")
            date_range = parse_date_range(meta.get("date_range"))
            has_nights = nights is not None
            has_date_range = meta.get("date_range") is not None
            if has_nights != has_date_range:
                self.error(readme, "nights and date_range must be provided together")
            if has_nights and (not isinstance(nights, int) or nights <= 0):
                self.error(readme, "scheduled hubs need positive integer nights")
            if has_date_range and date_range is None:
                self.error(readme, "date_range must be [start, end] with ISO dates")
            if date_range:
                start, end = date_range
                if not (trip.get("trip_start") <= start <= end <= trip.get("trip_end")):
                    self.error(readme, "date_range must be inside the canonical trip window")
                if isinstance(nights, int) and (end - start).days != nights:
                    self.error(readme, "nights must equal date_range end minus start")
                ranges.append((start, end, readme))
                scheduled_hubs += 1
                for day in itinerary_dates:
                    if not (start <= day < end):
                        self.error(hub / "itinerary", f"itinerary date outside sleep range: {day}")
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

    def check_questions(self, path: Path, body: str) -> None:
        if "UNVERIFIED" not in body:
            return
        questions = [
            line[5:].strip().lower()
            for line in body.splitlines()
            if line.strip().startswith("- [ ]")
        ]
        claims = [
            line.lower()
            for line in body.splitlines()
            if "UNVERIFIED" in line and not line.strip().startswith("- [ ]")
        ]
        for claim in claims:
            words = {word for word in re.findall(r"[a-z0-9]{4,}", claim) if word != "unverified"}
            if not any(len(words & set(re.findall(r"[a-z0-9]{4,}", question))) >= 1 for question in questions):
                self.error(path, "UNVERIFIED claim lacks a matching open question")

    def check_links(self) -> None:
        for path in ROOT.rglob("*.md"):
            if any(part in {".git", ".cursor"} for part in path.parts):
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
            if any(part in {".git", ".cursor"} for part in path.parts):
                continue
            text = path.read_text(encoding="utf-8")
            if "(assumed " in text:
                self.error(path, "legacy '(assumed ...)' marker is not allowed")

    def check_selected_links(self, path: Path, body: str, hub: Path) -> None:
        for target in MARKDOWN_LINK.findall(body):
            if target.startswith(("http://", "https://", "#", "mailto:")):
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
                        if ref_hub in attraction_ids and slug not in attraction_ids[ref_hub]:
                            self.error(path, f"unknown stable attraction reference {ref_hub}/{slug}")


def parse_yaml_block(text: str, validator: Validator, path: Path) -> dict:
    result: dict = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = parse_scalar(value.strip())
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
    start, end = map(date.fromisoformat, value)
    return (start, end) if start <= end else None


def find_references(target: str) -> list[tuple[Path, int, str]]:
    """Return Markdown lines that mention a target file."""
    target_path = (ROOT / target).resolve()
    if not target_path.exists() or target_path.suffix.lower() != ".md":
        raise ValueError(f"target must be an existing Markdown file: {target}")
    relative_name = target_path.relative_to(ROOT).as_posix()
    names = {target_path.name, relative_name}
    references = []
    for path in ROOT.rglob("*.md"):
        if path.resolve() == target_path or any(part in {".git", ".cursor"} for part in path.parts):
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
    args = parser.parse_args()
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
