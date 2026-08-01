# AGENTS.md — operating guide for AI agents

Git-backed Japan-trip plan (see [README.md](README.md)); keep it accurate and
consistent while executing [workflow.md](workflow.md).

## Authority order

Use this authority order: filesystem for existence and triage status; YAML
frontmatter for file metadata; root [constraints.md](constraints.md) for
trip-wide constants; README Status as a dashboard cache; this file for
operations, [schema.md](schema.md) for file shape, and [workflow.md](workflow.md)
for workstreams and dependencies.

## On session start

1. Read README Status, [workflow.md](workflow.md), [constraints.md](constraints.md),
   and [schema.md](schema.md).
2. Read [hubs/AGENTS.md](hubs/AGENTS.md) before working inside `hubs/`.
3. Check `hubs/graveyard/` before proposing a hub that may already have been rejected.
4. Choose a workstream whose local prerequisites are satisfied; unrelated hubs
   may be at different levels of readiness.
5. Run `python scripts/validate.py` after non-trivial edits and before treating
   a hub or the trip as complete.
6. Before editing Markdown, run `python scripts/validate.py --references <path>`.

## Operations

### Add a hub

1. Copy `hubs/_template/` to `hubs/<name>/` (kebab-case).
2. Fill its README frontmatter (`name`, `nights`, `date_range`, `base_location`).
3. Add the folder name to the `hubs:` list in the root README Status dashboard.

### Reject a hub

- Move the entire directory to `hubs/graveyard/<name>/`; this records the
  rejection. Exclude it from README Status `hubs:`; add context if useful.

### Add an attraction

1. Copy `hubs/<name>/attractions/_template.md` to `attractions/inbox/`.
2. Use a unique, lowercase kebab-case filename.
3. Use `null` for unknown frontmatter values; put unknowns under
   `## Open questions` as `- [ ]` items.
4. For popular attractions, check `booking_required`; if yes, set `book_by`.

### Triage an attraction

- `git mv` between `inbox/`, `shortlisted/`, `selected/`, and `skipped/`.
  **The folder alone indicates status.**
- A file entering `skipped/` must have `skip_reason` filled in.
- Research and prepare triage recommendations, but ask the user to confirm every
  final `selected` or `skipped` decision before moving the file.

### Reference attractions

- In prose and research notes, use stable `hub/slug` references (for example
  `kyoto/fushimi-inari`); do not use triage paths.
- Itinerary days instead use resolving relative links to
  `../attractions/selected/<slug>.md`.

### Schedule a hub

- Set `nights` and `date_range` together in the target hub README frontmatter.
- Partial schedules are allowed, but ranges may not overlap. Never allocate
  time to individual attractions.

### Draft itinerary days

1. Copy `_day-template.md` to `itinerary/YYYY-MM-DD.md`.
2. Fill `sunset:` from the target hub's constraints daylight table when known.
3. Schedule `daylight_sensitive: yes` activities early in the day.

## Facts, uncertainty, and open questions

- **Don't invent facts.** Source attraction/research claims in `research/`:
  `- <claim> — [<title>](URL) — accessed YYYY-MM-DD`.
- Unverifiable claims use exact `UNVERIFIED` plus a matching unchecked
  `## Open questions` item. Use `- [ ]`, one question per line.
- For ambiguous triage/scheduling, add a question instead of guessing.
- Record new trip-wide preferences or constraints as questions and ask the user.

## Hard rules

- Never delete attraction files; move ruled-out ideas to `skipped/` with
  `skip_reason`. Never delete rejected hubs; move them intact to `graveyard/`.
- Never edit `hubs/_template/` unless explicitly asked.
- Never change trip dates without user confirmation; root `constraints.md`
  frontmatter is canonical.
- Do not create parallel indexes; filesystem and frontmatter are the index.
- Keep the README Status dashboard current when the focus, next actions, or hub
  set changes.

## Validation

Run `python scripts/validate.py` and fix failures.

- It validates hub structure/metadata, attraction triage and `skip_reason`,
  unique IDs, links/references, source dates, `UNVERIFIED` questions, and the
  README Status dashboard.
- It validates every present schedule independently, rejects overlapping
  schedules, and checks full trip coverage when all active hubs are scheduled.
- It validates each present itinerary day against its own hub, schedule, links,
  and sunset metadata.

## Markdown dependency review

Before editing Markdown, run `python scripts/validate.py --references <path>`;
read every referring file, including templates and agent instructions; inspect
semantic references as well as links; update affected dependents; then run the
validator again. The reference output is only a discovery aid.

## Git hook

Enable the versioned hook once per clone:

```text
git config core.hooksPath .githooks
```

The hook runs `python scripts/validate.py` and the configured Markdown checks
before each commit.

## Commit conventions

Use small, logical commits:

```text
triage(kyoto): select fushimi-inari
triage(tokyo): skip robot-cafe — permanently closed
hub(osaka): allocate 4 nights
research(nikko): add autumn-foliage sources
itinerary(tokyo): draft 2026-10-20
docs: update workflow rules
```

## Glossary

- **Hub** — sleep base under `hubs/`; time is allocated per hub.
- **Attraction** — place/activity represented by one triaged Markdown file.
- **Triage** — `inbox → shortlisted → selected/skipped`.
- **Hub schedule** — the higher-level allocation of nights and dates to hubs.
- **Day itinerary** — the ordered plan for one date within one hub.
