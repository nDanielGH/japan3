---
name: triage-attractions
description: Review and classify Japan trip attraction records through inbox, shortlisted, selected, and skipped folders. Use when triaging attractions or preparing selection recommendations.
---

# Triage Attractions

Use this skill only within the Japan trip repository. Read `AGENTS.md`,
`hubs/AGENTS.md`, `workflow.md`, and `schema.md` before changing records.
This is a stage 2 procedure; check the current stage and ask before advancing
to stage 2 or reopening a completed stage.

## Procedure

1. Confirm the current stage permits triage and inspect the target hub's
   attraction collections.
2. Review each candidate's purpose, logistics, duration, daylight sensitivity,
   booking needs, sources, and open questions.
3. Check hub constraints and look for duplicate or conflicting attraction
   records.
4. Prepare a recommendation for each record:
   - `shortlisted` when it merits further consideration
   - `selected` when it is ready for itinerary planning
   - `skipped` when it should not be planned, with a specific reason
5. Present recommendations and unresolved questions to the user.
6. Wait for explicit user confirmation before moving any file into
   `selected/` or `skipped/`.
7. Use `git mv` between triage folders; the folder is the status.
8. For skipped records, fill `skip_reason`; for every other folder, keep it
   `null`.
9. Before editing Markdown, run
   `python scripts/validate.py --references <path>`, inspect dependents, then
   run `python scripts/validate.py`.

Never delete attraction files, invent missing facts, or assign itinerary time
to an attraction during triage.
