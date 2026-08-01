# Planning file schema

Machine-readable conventions for planning agents. The filesystem controls
collection membership/triage; frontmatter controls file metadata.

## General rules

- Use YAML frontmatter for structured metadata.
- Use `null` for an unknown value; do not leave a field value ambiguous.
- Dates use ISO format: `YYYY-MM-DD`.
- Folder and file IDs use lowercase kebab-case: `[a-z0-9]+(?:-[a-z0-9]+)*`.
- Filenames are unique within their collection and normally equal frontmatter
  `id`.
- Stable attraction references are exactly `hub/slug` (active hub and filename
  without `.md`), never triage paths. Itinerary links instead use
  `../attractions/selected/<slug>.md`.
- Source factual claims in the hub's `research/` collection:
  `- <claim> — [<title>](URL) — accessed YYYY-MM-DD`.
- `UNVERIFIED` claims need a semantically matching unchecked `## Open
  questions` item. Do not use legacy assumed markers.

## Root status dashboard

The YAML block under `## Status` in root `README.md` is a human-facing cache,
not a workflow state machine. It contains:

- `focus`: the current workstream or planning question.
- `hubs`: active folder names only; exclude `_template`, `graveyard`, and
  fixtures.
- `next_actions`: the next concrete actions, as a semicolon-separated string.
- `updated`: the last date the dashboard changed.

The validator requires `focus`, `hubs`, `next_actions`, and `updated`. The
filesystem and hub/attraction frontmatter remain authoritative for readiness.

## Hub frontmatter

```yaml
---
schema_version: 1
id: tokyo
name: Tokyo
nights: null
date_range: null
base_location: null
status: candidate
notes: null
---
```

`id` must match the folder. Every active hub needs `README.md`,
`constraints.md`, `attractions/`, `itinerary/`, and `research/`; attraction
subfolders are `inbox/`, `shortlisted/`, `selected/`, and `skipped/`.

`status` is `candidate`, `active`, or `complete`. A schedule is optional while
planning is partial; when present, `nights` and `date_range` must be provided
together. `nights` is a positive integer and `date_range` is `[start, end]`
within the trip window.
Its sleep interval is half-open `[start, end)`, so
`nights = (end date - start date).days`; hub ranges are contiguous, cover the
trip span, and do not overlap when all active hubs have schedules. Partial
schedules must not overlap. Rejected hubs remain under `hubs/graveyard/`.

## Attraction frontmatter

```yaml
---
schema_version: 1
id: fushimi-inari
name: Fushimi Inari Taisha
priority: high
area: southern kyoto
daylight_sensitive: yes
duration_estimate: 2h
booking_required: no
book_by: null
skip_reason: null
sources: []
notes: null
---
```

The parent folder alone indicates triage: `inbox`, `shortlisted`, `selected`, or
`skipped`. Skipped files need non-null `skip_reason`; others need `null`.
`id` must equal the filename stem and be unique within the hub. If
`booking_required: yes`, populate known `book_by` deadlines or add a question.

## Research notes

```yaml
---
schema_version: 1
id: autumn-foliage
topic: Autumn foliage
---
```

Research `id` must match the filename stem and be unique within the hub. Put
sources under `## Sources` and unresolved claims under `## Open questions`.

## Itinerary days

```yaml
---
schema_version: 1
date: 2026-10-19
hub: tokyo
sunset: "16:58"
---
```

Filename and `date` must be `YYYY-MM-DD` and match; `hub` must match the parent.
Dates must fall inside the hub's half-open sleep interval `[start, end)` when
that hub has a schedule. A partial plan may contain day files for only some
scheduled nights; once the trip is complete, every scheduled sleep night needs
one day file. A present itinerary day must include a sourced local sunset in
`HH:MM` and match the hub daylight table. A hub with `status: complete` must
have one valid day file for every scheduled sleep night. Only selected
attractions may be linked from an itinerary day, using exactly the relative
link form above.

## Source lines and open questions

A source line is a Markdown list item with one URL and exact
`accessed YYYY-MM-DD`; its claim must identify what it supports. Hub daylight
tables use inclusive `YYYY-MM-DD` or `YYYY-MM-DD to YYYY-MM-DD` ranges, local
`HH:MM` sunset values, and a source cell containing a URL plus
`accessed YYYY-MM-DD`. An unchecked question is one `- [ ]` line under
`## Open questions`. Matching is semantic: it must identify the unresolved
claim, not merely repeat `UNVERIFIED`.
