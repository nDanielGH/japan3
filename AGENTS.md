# Japan trip plans — guide for agents

## What this repo is

A personal planning workspace for a 32-night trip to Japan (arrive Narita
2026-10-18, depart 2026-11-19; see `constraints.md` and `trip.md`). The product
is a static GitHub Pages site, https://ndanielgh.github.io/japan3/, with one
mobile day-plan page per day. It is used on a phone during the trip, so pages
must keep working offline-ish, render correctly at 390 px wide, and never lose
the interactive features (live "Now" card, preview time, saved checklist,
expandable steps, image viewer with zoom).

## Source of truth and generated files

- `plan/week N/YYYY-MM-DD_DDD.md` is the **only** file you edit for a day.
  It is also the human-readable backup, so it must stay complete and readable.
- `plan/week N/YYYY-MM-DD_DDD.html` and the root `index.html` are **generated**
  by `python3 scripts/build.py`. Never edit them by hand, never write a day
  HTML page any other way, and never add links to `index.html` manually.
- `scripts/day_template.html` holds the shared design (the Tuesday 2026-10-20
  look, verbatim). Change it only when asked to change the design of every
  page, then rebuild all pages.
- `plan/assets/YYYY-MM-DD_DDD/` holds a day's images and PDFs. File names are
  kebab-case with no spaces. Reference them from the Markdown as
  `../assets/YYYY-MM-DD_DDD/file.png`.
- A day file without a `## Plan` section is a stub or free-form notes. It is
  not built and not listed in the index.
- `ideas/` and `research/` are reference material. Leave them alone unless the
  user asks for them.

## Workflow for any day change

1. Edit the day Markdown (format below).
2. `python3 scripts/build.py` regenerates stale pages and the index. A Claude
   Code hook in `.claude/settings.json` runs this automatically after edits.
3. `python3 scripts/check.py` must print `OK`. Fix every `ERROR`; never bypass
   it. The git pre-commit hook in `.githooks/` runs the same check and also
   fails when generated files were rebuilt but not staged.
4. `git add` the Markdown **and** the generated HTML/index, commit, push.
   Commit and push after every change.

## Rules

- Never invent a time, duration, platform, seat, price, or opening hour. If
  the user did not provide a time, ask; never guess or estimate unless
  explicitly asked.
- When a step's timing changes, update every subsequent step so the timeline
  stays consistent. Chained steps written as `+45m` move automatically;
  absolute steps do not. `check.py` fails when a step starts before the
  previous one ends.
- Hard departures (trains, buses, ropeways) carry the word `hard` in their
  kind label, e.g. `hard departure`; this drives the "Departs in" countdown.
- Warnings go in `!!! warning` blocks, which render in the `.warning` style.
- External links are plain Markdown links; the generator opens them in a new
  tab. Do not add HTML to the Markdown.
- Keep every file UTF-8 without a BOM. `check.py` scans for mojibake such as
  `â€“` and `Ã`; if it fires, the file was saved through a legacy code page.
- Do not reintroduce planning frameworks (schemas, hub folders, PWA runtime,
  validators beyond `scripts/check.py`). Earlier versions of this repo had
  them and they were removed on purpose.

## Day file format

```markdown
# 2026-10-24 — Saturday

title: Alpine Route Saturday
subtitle: Shinano Omachi → Kanazawa
index: Alpine Route → Kanazawa
footer: Times use Japan Standard Time. Check live transport before travel.
complete: Alpine day complete | Check in at KOKO HOTEL Korinbo.

## Before leaving

- [ ] Check Alpine Route operating status and weather.
- [ ] Pack **food and water** for the crossing.

## Plan

### Shinano Omachi → Ogizawa

**06:15–06:55** · Alpico Kotsu bus · hard departure

> One-line summary shown on the Now card.

Body paragraph with **bold** and [inline links](https://example.com).

- Bullet list.
- Another bullet.

1. Numbered list.

!!! warning **Make the connection:** 9 minutes to the bus.

**[Primary action](https://example.com/timetable)**
[Secondary action](https://example.com/map)
![Open segment map](../assets/2026-10-24_SAT/segment-map.png)

### Walk to the ropeway

**+45m** · Walking · about 45 min

> Starts when the previous step ends and lasts 45 minutes.

### Hotel

**21:15–open** · Short walk · flexible

> Open-ended final step; the timeline shows FREE.

## Quick references

- [Alpine Route timetable · Open PDF](../assets/2026-10-24_SAT/timetable.pdf)
- ![Segment map · Open image](../assets/2026-10-24_SAT/segment-map.png)
- [Official site · alpen-route.com](https://www.alpen-route.com/en/)
```

Details:

- Header lines before the first `##`: `title` and `subtitle` are required.
  `index` is the short label used on the index page (defaults to `title`).
  `footer` is the note at the bottom of the page. `complete` is
  `Title | Summary` for the Now card after the last step (optional).
- Sections allowed: `## Before leaving` (checklist, `- [ ]` lines only),
  `## Plan` (steps), `## Quick references` (one link or image per line).
  Checklist state is saved per device under the day's date.
- Each step is a `### Title`. The first line under it is the time line:
  `**HH:MM–HH:MM**`, `**HH:MM–open**`, `**HH:MM +45m**`, or `**+1h30m**`
  (chained to the previous step's end), followed by ` · kind label`.
  Append `[hard]` to the kind label to mark a hard departure without the word
  appearing in the label.
- The `> summary` line is required; it is the text on the Now card.
- A block of lines that are only links or images becomes the step's action
  buttons. `**[...](...)**` is the primary (filled) button. `![label](path)`
  opens the image in the viewer; everything else is an external link.
- Blank lines separate paragraphs, lists, warnings, and action blocks.
- Step ids are derived from titles; keep titles unique within a day.

## Other files

- `constraints.md`: fixed trip constants (dates, luggage, daylight).
- `trip.md`: route by night, hotels, bookings, decisions. Update it
  whenever a booking or sleeping location is decided.
- `scripts/build.py`, `scripts/check.py`, `scripts/day_template.html`: the
  whole toolchain. Python 3.9+, no dependencies.
- `.claude/skills/new-day/`: step-by-step procedure for adding a day.
