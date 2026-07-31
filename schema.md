# Planning file schema

This file defines the machine-readable conventions used by planning agents.
The filesystem is authoritative for collection membership and attraction triage
status; frontmatter is authoritative for metadata inside a file.

## General rules

- Use YAML frontmatter for structured metadata.
- Use `null` for an unknown value; do not leave a field value ambiguous.
- Dates use ISO format: `YYYY-MM-DD`.
- Folder and file IDs use lowercase kebab-case: `[a-z0-9]+(?:-[a-z0-9]+)*`.
- Filenames are unique within their collection and normally equal the
  frontmatter `id`.
- Stable attraction references use exactly `hub/slug`, where both parts are
  the active hub folder and attraction filename without `.md`. They never
  include a triage-folder path.
- Itinerary files are the exception: they use relative links into
  `../attractions/selected/<slug>.md`.
- Factual claims in attraction and research notes need a source line in the
  hub's `research/` collection:
  `- <claim> — [<title>](URL) — accessed YYYY-MM-DD`.
- A claim containing `UNVERIFIED` must have a semantically matching unchecked
  item under `## Open questions`. Do not use legacy assumed markers.

## Root status

The YAML block under `## Status` in the root `README.md` contains:

- `stage`: `0` before workflow stages begin, otherwise `1`–`5`.
- `stage_name`: the corresponding human-readable stage name.
- `hubs`: active hub folder names only; exclude `_template`, `graveyard`, and
  fixtures.
- `next_action`: the next concrete planning action.
- `updated`: the last date the status block changed.
- `stage_name` must match the stage name in [workflow.md](workflow.md).
- `hubs` is a YAML list, not a prose list, and must match active hub folders
  exactly.

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

`id` must match the hub folder name. Every active hub must contain exactly the
expected top-level paths: `README.md`, `constraints.md`, `attractions/`,
`itinerary/`, and `research/`; its attraction subfolders are `inbox/`,
`shortlisted/`, `selected/`, and `skipped/`.

`status` is one of `candidate`, `active`, or `complete`. At stage 4 and later,
`nights` is a positive integer and `date_range` is two ISO dates in
`[trip_start, trip_end]`, written as `[start, end]`. The range represents
check-in/sleep start through checkout/departure: its interval is half-open
`[start, end)`, so `nights = (end date - start date).days`. Hub ranges are
contiguous by sharing a transfer/check-in date, and their intervals cover the
canonical trip span without overlap.
Rejected hub directories are kept intact under `hubs/graveyard/` and are not
part of the active hub set.

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

The file's parent folder is the only triage status:
`inbox`, `shortlisted`, `selected`, or `skipped`. A skipped file must have a
non-null `skip_reason`; other folders must have `skip_reason: null`. The
frontmatter `id` must equal the filename stem and be unique within the hub.
If `booking_required: yes`, `book_by` should be populated when a deadline is
known; if the deadline is unknown, add an open question.

## Research notes

```yaml
---
schema_version: 1
id: autumn-foliage
topic: Autumn foliage
---
```

Research note IDs must match their filename stems and be unique within the
hub. Source lines belong under `## Sources`; unresolved claims belong under
`## Open questions`.

## Itinerary days

```yaml
---
schema_version: 1
date: 2026-10-19
hub: tokyo
sunset: "16:58"
---
```

The filename must be `YYYY-MM-DD.md` and match `date`; `hub` must match the
parent hub. Itinerary dates must fall inside the hub's half-open sleep interval
`[start, end)`, and stage 5 requires exactly one day file per sleep night in
all hub ranges. Checkout/transfer dates are represented by the next hub's
itinerary when applicable, not duplicated in both hubs.
`sunset` is `null` until the hub daylight table has a sourced value; before
stage 5 completion it must be a local time in `HH:MM`. Only selected
attractions may be linked from an itinerary day, using the relative link form
above.

## Source lines and open questions

A source line is a Markdown list item containing one URL and an access date in
the exact `accessed YYYY-MM-DD` form. The claim text before the em dash should
be specific enough to identify what it supports. An unchecked question is one
line beginning `- [ ]` under an `## Open questions` heading. Matching is
semantic: the question must identify the same unresolved claim, not merely
repeat the token `UNVERIFIED`.
