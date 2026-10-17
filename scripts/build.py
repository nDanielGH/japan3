#!/usr/bin/env python3
"""Build the day-plan HTML pages and the root index.html from Markdown sources.

Usage:
    python3 scripts/build.py            # write every page that is out of date
    python3 scripts/build.py --check    # exit 1 and list pages that are stale or broken

Sources:  plan/week N/YYYY-MM-DD_DDD.md   (format documented in AGENTS.md)
Outputs:  plan/week N/YYYY-MM-DD_DDD.html and index.html
Template: scripts/day_template.html (the Tuesday 2026-10-20 design, verbatim)

No third-party dependencies. Python 3.9+.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "plan"
TEMPLATE = ROOT / "scripts" / "day_template.html"
INDEX = ROOT / "index.html"
JST = dt.timezone(dt.timedelta(hours=9))

DAY_FILE = re.compile(r"^(\d{4}-\d{2}-\d{2})_+([A-Z]{3})\.md$")
TIME_LINE = re.compile(r"^\*\*(?P<time>[^*]+)\*\*(?:\s*·\s*(?P<kind>.*))?$")
HHMM = re.compile(r"^(\d{1,2}):(\d{2})$")
DURATION = re.compile(r"^\+\s*(?:(\d+)\s*h)?\s*(?:(\d+)\s*m(?:in)?)?$")
URL = r"(?:[^()\s]|\([^()\s]*\))+"  # allows one level of balanced parentheses inside a URL
LINK_ONLY = re.compile(r"^(?P<primary>\*\*)?(?P<img>!)?\[(?P<label>[^\]]+)\]\((?P<url>" + URL + r")\)(?(primary)\*\*)$")
INLINE_LINK = re.compile(r"\[([^\]]+)\]\((" + URL + r")\)")
INLINE_BOLD = re.compile(r"\*\*(.+?)\*\*")
INLINE_CODE = re.compile(r"`([^`]+)`")


class DayError(Exception):
    """A day source file is malformed. The message names the file and the problem."""


@dataclass
class Action:
    label: str
    url: str
    image: bool = False
    primary: bool = False


@dataclass
class Step:
    title: str
    kind: str
    hard: bool
    start: dt.datetime
    end: dt.datetime | None  # None means open-ended ("FREE")
    summary: str
    body: list[str] = field(default_factory=list)  # rendered HTML blocks
    actions: list[Action] = field(default_factory=list)
    step_id: str = ""


@dataclass
class Resource:
    title: str
    small: str
    url: str
    image: bool = False


@dataclass
class Day:
    path: Path
    date: dt.date
    meta: dict[str, str]
    checklist: list[str]
    steps: list[Step]
    resources: list[Resource]

    @property
    def html_path(self) -> Path:
        return self.path.with_suffix(".html")

    @property
    def weekday(self) -> str:
        return self.date.strftime("%A")

    @property
    def long_date(self) -> str:
        return f"{self.date.day} {self.date.strftime('%B %Y')}"

    @property
    def short_date(self) -> str:
        return f"{self.date.day} {self.date.strftime('%b %Y')}"


# ---------------------------------------------------------------- helpers

def slugify(text: str, used: set[str] | None = None) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "item"
    slug = re.sub(r"-+", "-", slug)
    if used is not None:
        base, n = slug, 2
        while slug in used:
            slug = f"{base}-{n}"
            n += 1
        used.add(slug)
    return slug


def is_external(url: str) -> bool:
    return url.startswith(("http://", "https://"))


def inline(text: str) -> str:
    """Render inline Markdown: **bold**, `code`, [text](url). Everything else is escaped."""
    out, pos = [], 0
    tokens = sorted(
        [(m.start(), m.end(), "link", m) for m in INLINE_LINK.finditer(text)]
        + [(m.start(), m.end(), "bold", m) for m in INLINE_BOLD.finditer(text)]
        + [(m.start(), m.end(), "code", m) for m in INLINE_CODE.finditer(text)]
    )
    for start, end, kind, m in tokens:
        if start < pos:
            continue
        out.append(html.escape(text[pos:start]))
        if kind == "link":
            out.append(
                f'<a href="{html.escape(m.group(2), quote=True)}" target="_blank" rel="noopener">{inline(m.group(1))}</a>'
            )
        elif kind == "bold":
            out.append(f"<strong>{inline(m.group(1))}</strong>")
        else:
            out.append(f"<code>{html.escape(m.group(1))}</code>")
        pos = end
    out.append(html.escape(text[pos:]))
    return "".join(out)


def attr(text: str) -> str:
    return html.escape(text, quote=True)


def parse_hhmm(token: str, date: dt.date, where: str) -> dt.datetime:
    m = HHMM.match(token.strip())
    if not m:
        raise DayError(f"{where}: bad time {token!r}; use HH:MM")
    return dt.datetime(date.year, date.month, date.day, int(m.group(1)), int(m.group(2)), tzinfo=JST)


def parse_duration(token: str, where: str) -> dt.timedelta:
    m = DURATION.match(token.strip())
    if not m or not (m.group(1) or m.group(2)):
        raise DayError(f"{where}: bad duration {token!r}; use +45m or +1h30m")
    return dt.timedelta(hours=int(m.group(1) or 0), minutes=int(m.group(2) or 0))


def iso(moment: dt.datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%S+09:00")


def hm(moment: dt.datetime) -> str:
    return moment.strftime("%H:%M")


# ---------------------------------------------------------------- parsing

def split_sections(lines: list[str]) -> tuple[list[str], dict[str, list[str]]]:
    """Return (front lines before the first '## ', {section heading: lines})."""
    front: list[str] = []
    sections: dict[str, list[str]] = {}
    current: list[str] | None = None
    for line in lines:
        if line.startswith("## "):
            current = sections.setdefault(line[3:].strip().lower(), [])
            continue
        (front if current is None else current).append(line)
    return front, sections


def parse_meta(front: list[str], where: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    for line in front:
        if not line.strip() or line.startswith("# "):
            continue
        if ":" not in line:
            raise DayError(f"{where}: unexpected line before the first section: {line!r}")
        key, _, value = line.partition(":")
        meta[key.strip().lower()] = value.strip()
    for required in ("title", "subtitle"):
        if not meta.get(required):
            raise DayError(f"{where}: missing '{required}:' line in the header")
    return meta


def parse_checklist(lines: list[str], where: str) -> list[str]:
    items = []
    for line in lines:
        if not line.strip():
            continue
        m = re.match(r"^- \[[ xX]\] (.+)$", line)
        if not m:
            raise DayError(f"{where}: 'Before leaving' only accepts '- [ ] item' lines, got {line!r}")
        items.append(m.group(1).strip())
    return items


def parse_resources(lines: list[str], where: str) -> list[Resource]:
    items = []
    for line in lines:
        if not line.strip():
            continue
        m = re.match(r"^- (!?)\[([^\]]+)\]\((" + URL + r")\)$", line)
        if not m:
            raise DayError(f"{where}: 'Quick references' only accepts '- [Title · Subtitle](url)' lines, got {line!r}")
        image = m.group(1) == "!"
        title, _, small = m.group(2).partition(" · ")
        if not small:
            small = "Open image" if image else "Open link"
        items.append(Resource(title.strip(), small.strip(), m.group(3), image))
    return items


def parse_steps(lines: list[str], date: dt.date, where: str) -> list[Step]:
    """Parse '### Title' blocks. Blank lines separate blocks inside a step body."""
    chunks: list[tuple[str, list[str]]] = []
    for line in lines:
        if line.startswith("### "):
            chunks.append((line[4:].strip(), []))
        elif line.startswith("#"):
            raise DayError(f"{where}: only '### ' headings are allowed inside '## Plan', got {line!r}")
        elif chunks:
            chunks[-1][1].append(line)
        elif line.strip():
            raise DayError(f"{where}: text before the first '### ' step: {line!r}")

    steps: list[Step] = []
    used_ids: set[str] = set()
    previous_end: dt.datetime | None = None
    for title, body_lines in chunks:
        swhere = f"{where} › {title}"
        blocks = [b for b in "\n".join(body_lines).split("\n\n")]
        blocks = [b.strip("\n") for b in blocks if b.strip()]
        if not blocks or not TIME_LINE.match(blocks[0].strip()):
            raise DayError(f"{swhere}: first line after the heading must be a time line such as '**07:50–08:49** · Bus · hard departure'")
        tm = TIME_LINE.match(blocks[0].strip())
        start, end = parse_time_spec(tm.group("time"), date, previous_end, swhere)
        kind = (tm.group("kind") or "").strip()
        hard = False
        if kind.endswith("[hard]"):
            hard, kind = True, kind[: -len("[hard]")].strip(" ·")
        elif re.search(r"\bhard\b", kind, re.I):
            hard = True
        if not kind:
            raise DayError(f"{swhere}: add a kind label after the time, e.g. '· Walking · about 25 min'")

        summary = ""
        rendered: list[str] = []
        actions: list[Action] = []
        for block in blocks[1:]:
            if block.startswith("> ") and not summary:
                summary = " ".join(l[2:].strip() if l.startswith("> ") else l.strip() for l in block.splitlines())
                continue
            if block.startswith("!!! warning"):
                text = block[len("!!! warning"):].strip()
                rendered.append(f'<p class="warning">{inline(" ".join(text.split()))}</p>')
                continue
            if all(LINK_ONLY.match(l.strip()) for l in block.splitlines()):
                for l in block.splitlines():
                    m = LINK_ONLY.match(l.strip())
                    actions.append(Action(m.group("label"), m.group("url"), bool(m.group("img")), bool(m.group("primary"))))
                continue
            if all(re.match(r"^- ", l) for l in block.splitlines()):
                rendered.append("<ul>" + "".join(f"<li>{inline(l[2:].strip())}</li>" for l in block.splitlines()) + "</ul>")
                continue
            if all(re.match(r"^\d+\. ", l) for l in block.splitlines()):
                rendered.append("<ol>" + "".join(f"<li>{inline(l.split('. ', 1)[1].strip())}</li>" for l in block.splitlines()) + "</ol>")
                continue
            if block.lstrip().startswith(("- ", "1. ", "> ", "!!!")):
                raise DayError(f"{swhere}: mixed block; separate lists, quotes and warnings from paragraphs with a blank line:\n{block}")
            rendered.append(f"<p>{inline(' '.join(block.split()))}</p>")
        if not summary:
            raise DayError(f"{swhere}: add a one-line '> summary' under the time line (shown on the Now card)")
        steps.append(Step(title, kind, hard, start, end, summary, rendered, actions, slugify(title, used_ids)))
        previous_end = end if end else start
    return steps


def parse_time_spec(spec: str, date: dt.date, previous_end: dt.datetime | None, where: str) -> tuple[dt.datetime, dt.datetime | None]:
    spec = spec.strip().replace("—", "–").replace(" - ", "–")
    if spec.startswith("+"):
        if previous_end is None:
            raise DayError(f"{where}: the first step cannot use a relative '+duration' time")
        return previous_end, previous_end + parse_duration(spec, where)
    if "–" in spec:
        a, b = (p.strip() for p in spec.split("–", 1))
        start = parse_hhmm(a, date, where)
        if b.lower() == "open":
            return start, None
        end = parse_hhmm(b, date, where)
        if end < start:
            raise DayError(f"{where}: end {b} is before start {a}")
        return start, end
    if " +" in spec or "+" in spec:
        a, _, d = spec.partition("+")
        start = parse_hhmm(a, date, where)
        return start, start + parse_duration("+" + d, where)
    raise DayError(f"{where}: time must be 'HH:MM–HH:MM', 'HH:MM–open', 'HH:MM +45m' or '+45m'")


def parse_day(path: Path) -> Day | None:
    """Return the Day, or None when the file is an empty stub (heading only)."""
    m = DAY_FILE.match(path.name)
    if not m:
        raise DayError(f"{path}: file name must look like 2026-10-20_TUE.md")
    date = dt.date.fromisoformat(m.group(1))
    if date.strftime("%a").upper() != m.group(2):
        raise DayError(f"{path}: {date} is a {date.strftime('%A')}, but the file name says {m.group(2)}")
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise DayError(f"{path}: remove the UTF-8 byte-order mark")
    text = raw.decode("utf-8")
    lines = text.splitlines()
    where = str(path.relative_to(ROOT))
    front, sections = split_sections(lines)
    if not sections:
        return None  # stub or free-form notes without a '## Plan' section: nothing to build
    meta = parse_meta(front, where)
    unknown = set(sections) - {"before leaving", "plan", "quick references"}
    if unknown:
        raise DayError(f"{where}: unknown section(s) {sorted(unknown)}; allowed: Before leaving, Plan, Quick references")
    steps = parse_steps(sections.get("plan", []), date, where)
    if not steps:
        raise DayError(f"{where}: '## Plan' needs at least one '### ' step")
    return Day(
        path=path,
        date=date,
        meta=meta,
        checklist=parse_checklist(sections.get("before leaving", []), where),
        steps=steps,
        resources=parse_resources(sections.get("quick references", []), where),
    )


# ---------------------------------------------------------------- rendering

def render_action(a: Action) -> str:
    cls = "action primary" if a.primary else "action"
    if a.image:
        return (f'<button class="{cls} image-link" type="button" data-image="{attr(a.url)}" '
                f'data-label="{attr(a.label)}">{html.escape(a.label)}</button>')
    arrow = " ↗"
    return f'<a class="{cls}" href="{attr(a.url)}" target="_blank" rel="noopener">{html.escape(a.label)}{arrow}</a>'


def render_step(step: Step) -> str:
    end_attr = f'\n          data-end="{iso(step.end)}"' if step.end else ""
    end_label = hm(step.end) if step.end else "FREE"
    body = "\n".join(f"            {b}" for b in step.body)
    actions = ""
    if step.actions:
        actions = ('\n            <div class="actions">\n'
                   + "\n".join(f"              {render_action(a)}" for a in step.actions)
                   + "\n            </div>")
    return f"""        <details class="step" id="{step.step_id}"
          data-start="{iso(step.start)}"{end_attr}
          data-title="{attr(step.title)}"
          data-summary="{attr(step.summary)}"
          data-hard="{'true' if step.hard else 'false'}">
          <summary>
            <span class="time">{hm(step.start)}<br>{end_label}</span>
            <span><span class="step-title">{html.escape(step.title)}</span><span class="kind">{inline(step.kind)}</span></span>
          </summary>
          <div class="step-body">
{body}{actions}
          </div>
        </details>"""


def render_resource(r: Resource) -> str:
    if r.image:
        return (f'<button class="resource image-link" type="button" data-image="{attr(r.url)}" '
                f'data-label="{attr(r.title)}">{html.escape(r.title)}<small>{html.escape(r.small)}</small></button>')
    return (f'<a class="resource" href="{attr(r.url)}" target="_blank" rel="noopener">'
            f'{html.escape(r.title)}<small>{html.escape(r.small)} ↗</small></a>')


def preview_options(day: Day) -> str:
    first, last = day.steps[0], day.steps[-1]
    options = [(first.start - dt.timedelta(minutes=30), "Before departure")]
    options += [(s.start, s.title) for s in day.steps]
    if last.end:
        options.append((last.end + dt.timedelta(minutes=10), "Day complete"))
    return "\n".join(
        f'          <option value="{iso(t)}">{hm(t)} · {html.escape(label)}</option>' for t, label in options
    )


def render_body(day: Day) -> str:
    first = day.steps[0]
    used: set[str] = set()
    checks = "\n".join(
        f'        <label class="check-row"><input data-check="{slugify(" ".join(item.split()[:4]), used)}" type="checkbox">'
        f"<span>{inline(item)}</span></label>"
        for item in day.checklist
    ) or '        <p class="section-note">Nothing to prepare for this day.</p>'
    resources = "\n".join(f"        {render_resource(r)}" for r in day.resources) \
        or '        <p class="section-note">No quick references for this day.</p>'
    footer = day.meta.get("footer", "Times use Japan Standard Time. Check live transport and weather information before travel.")
    first_time = f"{hm(first.start)}–{hm(first.end)}" if first.end else f"{hm(first.start)} onward"
    return f"""    <header id="top">
      <p class="eyebrow">Japan · Day plan</p>
      <h1>{html.escape(day.meta['title'])}</h1>
      <p class="date">{day.long_date} · {html.escape(day.meta['subtitle'])}</p>
    </header>

    <article class="now-card" aria-live="polite">
      <div class="now-top">
        <span class="status-label"><span class="status-dot"></span><span id="statusLabel">UP NEXT</span></span>
        <time id="clock">Japan time</time>
      </div>
      <h2 id="nowTitle">{html.escape(first.title)}</h2>
      <p id="nowTime">{first_time}</p>
      <p id="nowSummary">{html.escape(first.summary)}</p>
      <div id="countdown" class="countdown">Day plan for {day.long_date}</div><br>
      <a id="nowButton" class="now-button" href="#{first.step_id}">View first step ↓</a>
    </article>

    <details class="preview">
      <summary>Preview the itinerary at another time</summary>
      <div class="preview-controls">
        <select id="previewTime" aria-label="Preview itinerary time">
          <option value="">Live Japan time</option>
{preview_options(day)}
        </select>
        <button id="liveButton" class="small-button" type="button">Live</button>
      </div>
    </details>

    <section id="prepare">
      <div class="section-heading">
        <h2>Before leaving</h2>
        <span class="section-note">Saved on this device</span>
      </div>
      <div class="prep-list">
{checks}
      </div>
    </section>

    <section id="timeline-section">
      <div class="section-heading">
        <h2>Timeline</h2>
        <span class="section-note">Tap a step for details</span>
      </div>
      <div class="timeline" id="timeline">
{chr(10).join(render_step(s) for s in day.steps)}
      </div>
    </section>

    <section id="resources">
      <div class="section-heading">
        <h2>Quick references</h2>
      </div>
      <div class="resource-grid">
{resources}
      </div>
    </section>

    <p class="footer-note">{inline(footer)}</p>"""


def render_day(day: Day, template: str) -> str:
    last = day.steps[-1]
    complete_title, _, complete_summary = day.meta.get("complete", "").partition(" | ")
    config = {
        "date": day.date.isoformat(),
        "dayEnd": iso(dt.datetime(day.date.year, day.date.month, day.date.day, 23, 59, tzinfo=JST)),
        "complete": {
            "title": complete_title.strip() or f"{day.meta['title']} complete",
            "time": f"Finished at {hm(last.end)}" if last.end else f"Last step began {hm(last.start)}",
            "summary": complete_summary.strip() or "All scheduled steps for today are finished.",
        },
    }
    page = (template
            .replace("{{TITLE}}", html.escape(f"{day.meta['title']} · {day.short_date}"))
            .replace("{{BODY}}", render_body(day))
            .replace("{{CONFIG_JSON}}", json.dumps(config, ensure_ascii=False)))
    return page


INDEX_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#173f35">
  <title>Japan Trip Plans</title>
  <style>
    :root {
      color-scheme: light dark;
      --bg: #f4f2ea;
      --surface: #fffdf7;
      --ink: #17201d;
      --muted: #60706a;
      --green: #173f35;
      --gold: #b97922;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      padding: 24px;
      background: var(--bg);
      color: var(--ink);
      font: 16px/1.5 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    main {
      width: min(680px, 100%);
      margin: 8vh auto;
      padding: 28px;
      background: var(--surface);
      border: 1px solid rgba(23, 63, 53, .12);
      border-radius: 20px;
      box-shadow: 0 8px 28px rgba(23, 63, 53, .10);
    }

    h1 { margin: 0 0 8px; color: var(--green); }
    p { color: var(--muted); }

    a {
      display: block;
      margin-top: 20px;
      padding: 16px 18px;
      border-radius: 12px;
      background: var(--green);
      color: #fff;
      font-weight: 700;
      text-decoration: none;
    }

    a:hover { background: var(--gold); }
  </style>
</head>
<body>
  <main>
    <h1>Japan Trip Plans</h1>
    <p>Day-by-day itineraries and travel references.</p>
{links}
  </main>
</body>
</html>
"""


def render_index(days: list[Day]) -> str:
    links = []
    for day in sorted(days, key=lambda d: d.date):
        href = day.html_path.relative_to(ROOT).as_posix().replace(" ", "%20")
        label = day.meta.get("index") or day.meta["title"]
        links.append(f'    <a href="{attr(href)}">{day.weekday}, {day.long_date} · {html.escape(label)}</a>')
    return INDEX_TEMPLATE.replace("{links}", "\n".join(links))


# ---------------------------------------------------------------- driver

def day_sources() -> list[Path]:
    return sorted(p for p in PLAN.glob("week */*.md"))


def build_all() -> tuple[dict[Path, str], list[str]]:
    """Return ({output path: content}, [error messages]) without writing anything."""
    template = TEMPLATE.read_text(encoding="utf-8")
    outputs: dict[Path, str] = {}
    errors: list[str] = []
    days: list[Day] = []
    for src in day_sources():
        try:
            day = parse_day(src)
        except DayError as exc:
            errors.append(str(exc))
            continue
        if day is None:
            continue
        days.append(day)
        outputs[day.html_path] = render_day(day, template)
    outputs[INDEX] = render_index(days)
    return outputs, errors


def main(argv: list[str]) -> int:
    check = "--check" in argv
    outputs, errors = build_all()
    for message in errors:
        print(f"ERROR {message}", file=sys.stderr)
    stale = []
    for path, content in outputs.items():
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == content:
            continue
        stale.append(path)
        if not check:
            path.write_text(content, encoding="utf-8", newline="\n")
            print(f"wrote {path.relative_to(ROOT)}")
    if check:
        for path in stale:
            print(f"STALE {path.relative_to(ROOT)} (run: python3 scripts/build.py)", file=sys.stderr)
        return 1 if (errors or stale) else 0
    if not stale and not errors:
        print("up to date")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
