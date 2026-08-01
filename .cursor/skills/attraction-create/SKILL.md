---
name: attraction-create
description: Create a researched-or-unresearched attraction idea in a specific Japan-trip hub inbox. Use when adding a place or activity for later triage.
disable-model-invocation: true
---

# Create attraction idea

## Preconditions

- Require an existing active hub and a proposed attraction name.
- Read the hub rules, attraction template, `AGENTS.md`, and `schema.md`.
- Confirm the slug is unique within that hub and is lowercase kebab-case.
- Follow the repository Mutation protocol. The owned path is the new inbox
  record; stop if it overlaps existing user changes.

## Allowed operation

1. Copy `hubs/<hub>/attractions/_template.md` to
   `hubs/<hub>/attractions/inbox/<slug>.md`.
2. Run `python scripts/validate.py --references <new-file>` before editing the
   new Markdown record.
3. Fill known frontmatter fields only. Use `null` for unknown values and keep
   `skip_reason: null`.
4. Record user-provided purpose, activity, logistics, and open questions.
5. Do not claim that an attraction is selected, skipped, booked, or researched
   unless the repository contains support for that claim.
6. Run `python scripts/validate.py` and the configured Markdown checks against
   the new record. If any check fails, restore the new record's owned path to
   its pre-operation state and report the failure.

Create exactly one inbox record. Do not move it to `shortlisted/` or
`selected/`, and do not create duplicate indexes. If validation fails, stop and
report the failure without making additional changes.
