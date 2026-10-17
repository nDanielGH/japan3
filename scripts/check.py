#!/usr/bin/env python3
"""Validate the day plans. Exit 0 when everything is consistent.

Usage:
    python3 scripts/check.py            # full check, human output, exit 1 on problems
    python3 scripts/check.py --staged   # also fail if generated files differ from the git index (pre-commit)
    python3 scripts/check.py --hook     # Claude Code PostToolUse hook: reads the tool JSON on stdin,
                                        # rebuilds when a plan file changed, exit 2 with messages on problems

Checks:
  * every day Markdown parses (format in AGENTS.md) and its HTML + index.html are up to date
  * times are HH:MM, every step ends after it starts, and no step starts before the previous one ends
  * every local asset referenced from a day exists, lives under plan/assets/, and has no spaces in its name
  * every other link is http(s)
  * day Markdown and generated HTML are valid UTF-8 without a BOM or mojibake
  * generated pages still contain the interactive features (timeline, checklist, viewer, zoom, preview)
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

ROOT = build.ROOT
MOJIBAKE = re.compile("Ã.|â€.|Â.|ï»¿|�")
REQUIRED_MARKERS = [
    'id="timeline"', 'class="step"', 'data-check=', 'id="imageViewer"', 'id="zoomOut"',
    'id="zoomReset"', 'id="zoomIn"', 'id="previewTime"', 'class="bottom-nav"', 'localStorage',
]


def check(staged: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    notes: list[str] = []

    outputs, build_errors = build.build_all()
    errors += build_errors
    for path, content in outputs.items():
        rel = path.relative_to(ROOT)
        if not path.exists():
            errors.append(f"{rel}: missing; run python3 scripts/build.py")
        elif path.read_text(encoding="utf-8") != content:
            errors.append(f"{rel}: stale; run python3 scripts/build.py")
        if path != build.INDEX:
            missing = [m for m in REQUIRED_MARKERS if m not in content]
            if missing:
                errors.append(f"{rel}: generated page lacks {missing}; the template is damaged")

    for src in build.day_sources():
        rel = src.relative_to(ROOT)
        try:
            day = build.parse_day(src)
        except build.DayError:
            continue  # already reported by build_all
        if day is None:
            notes.append(f"{rel}: no '## Plan' section, not built")
            continue
        previous = None
        for step in day.steps:
            if previous and step.start < previous.start:
                errors.append(f"{rel} › {step.title}: starts before the previous step")
            if previous and previous.end and step.start < previous.end:
                errors.append(f"{rel} › {step.title}: starts at {build.hm(step.start)} but '{previous.title}' ends at {build.hm(previous.end)}")
            previous = step
        urls = [a.url for s in day.steps for a in s.actions] + [r.url for r in day.resources]
        urls += re.findall(r"\]\(([^)\s]+)\)", src.read_text(encoding="utf-8"))
        for url in dict.fromkeys(urls):
            if build.is_external(url):
                continue
            if url.startswith(("mailto:", "tel:", "#")):
                continue
            target = (src.parent / url.replace("%20", " ")).resolve()
            if " " in url or "%20" in url:
                errors.append(f"{rel}: asset path has spaces, rename it to kebab-case: {url}")
            if not target.exists():
                errors.append(f"{rel}: missing asset {url}")
            elif build.PLAN / "assets" not in target.parents:
                errors.append(f"{rel}: asset must live under plan/assets/: {url}")

    for path in list(build.PLAN.rglob("*.md")) + list(build.PLAN.rglob("*.html")) + [build.INDEX]:
        raw = path.read_bytes()
        rel = path.relative_to(ROOT)
        if raw.startswith(b"\xef\xbb\xbf"):
            errors.append(f"{rel}: has a UTF-8 BOM")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"{rel}: not valid UTF-8 ({exc})")
            continue
        m = MOJIBAKE.search(text)
        if m:
            line = text.count("\n", 0, m.start()) + 1
            errors.append(f"{rel}:{line}: looks like mojibake near {m.group(0)!r}; the file was saved through a legacy code page")

    if staged:
        generated = [str(p.relative_to(ROOT)) for p in outputs]
        diff = subprocess.run(["git", "diff", "--name-only", "--"] + generated, cwd=ROOT, capture_output=True, text=True)
        for name in diff.stdout.split():
            errors.append(f"{name}: generated file changed but not staged; run git add")
    return errors, notes


def main(argv: list[str]) -> int:
    if "--hook" in argv:
        try:
            payload = json.load(sys.stdin)
        except Exception:
            payload = {}
        file_path = str((payload.get("tool_input") or {}).get("file_path") or "")
        if not file_path:
            return 0
        try:
            rel = Path(file_path).resolve().relative_to(ROOT).as_posix()
        except ValueError:
            return 0
        if not (rel.startswith(("plan/", "scripts/")) or rel == "index.html"):
            return 0
        if rel.endswith(".md") or rel.startswith("scripts/"):
            build.main([])  # rebuild silently so the HTML never lags the Markdown
        errors, _ = check()
        if errors:
            print("Day-plan check failed:\n  " + "\n  ".join(errors), file=sys.stderr)
            return 2
        return 0

    errors, notes = check(staged="--staged" in argv)
    if notes:
        print(f"note  {len(notes)} day file(s) have no '## Plan' section yet and were not built")
    for err in errors:
        print(f"ERROR {err}")
    print("OK: day plans are consistent" if not errors else f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
