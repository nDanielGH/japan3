---
name: attraction-triage
description: Classify a Japan-trip attraction as shortlisted, selected, or skipped using explicit criteria and confirmation boundaries. Use when changing an attraction's triage status.
disable-model-invocation: true
---

# Triage attraction

## Preconditions

- Require one existing attraction in `inbox/` or `shortlisted/`.
- Require an explicit target status: `shortlisted`, `selected`, or `skipped`.
- Read the attraction, related research, hub constraints, and `schema.md`.
- State the criteria, evidence, uncertainty, and conflicts behind the proposal.
- Run `python scripts/validate.py --references <attraction-file>` before
  editing its Markdown.
- Follow the repository Mutation protocol. The owned paths are the source
  attraction and its target triage path; stop if either overlaps existing user
  changes.

## Decision boundaries

- `shortlisted`: reversible consideration; confirmation is not required.
- `selected`: require explicit user confirmation before moving the file.
- `skipped`: require a specific reason and explicit user confirmation before
  setting `skip_reason` and moving the file.

## Allowed operation

1. Check that the attraction ID matches its filename and remains unique within
   the hub.
2. Preserve the attraction contents and move it to the target triage folder.
   Use `git mv` for tracked files and a normal filesystem move for new,
   untracked records.
3. Keep `skip_reason: null` outside `skipped/`; set it only to the approved
   reason inside `skipped/`.
4. Run `python scripts/validate.py` and the configured Markdown checks against
   the moved attraction. If any check fails, restore the source and target
   paths from the pre-operation backup and report the failure.

Do not assign dates, create itinerary days, delete records, overwrite an
existing destination, or silently resolve open questions.
