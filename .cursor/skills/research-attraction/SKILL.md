---
name: research-attraction
description: Research a Japan trip attraction and create a sourced inbox record with logistics, uncertainty, and open questions. Use when adding, researching, or documenting an attraction.
---

# Research Attraction

Use this skill only within the Japan trip repository. Read the applicable
`AGENTS.md`, `schema.md`, root `constraints.md`, and hub constraints first.
This is a repeatable workstream for any active hub. Check the target hub's
local readiness and proceed independently of other hubs.

## Procedure

1. Confirm the target hub exists and is an active hub, not `_template` or
   `graveyard`.
2. Check the hub's `attractions/inbox/`, `shortlisted/`, `selected/`, and
   `skipped/` folders for duplicate ideas.
3. Copy `hubs/<hub>/attractions/_template.md` to
   `hubs/<hub>/attractions/inbox/<slug>.md`.
4. Use a unique lowercase kebab-case slug and set `id` to the filename stem.
5. Copy `hubs/<hub>/research/_note-template.md` to a uniquely named
   `hubs/<hub>/research/<topic>.md` note, and fill its `id` and `topic`
   frontmatter.
6. Fill known metadata. Use `null` for unknown values; if
   `booking_required: yes`, populate `book_by` when known or add an open
   question.
7. Put sourced factual claims about the attraction in the research note using:
   `- <claim> — [<title>](URL) — accessed YYYY-MM-DD`.
8. Use exact `UNVERIFIED` for unresolved claims and add a semantically
   matching unchecked `- [ ]` question under `## Open questions`.
9. Use stable `hub/slug` references in prose and research notes, never triage
   paths.
10. Run `python scripts/validate.py --references <new-file>` before editing
   related Markdown, inspect the referring files, then run
   `python scripts/validate.py`.

Do not move the attraction to `selected/` or `skipped/`; triage decisions
require user confirmation.
