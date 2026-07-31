---
name: draft-itinerary-day
description: Draft and validate one Japan trip itinerary day from selected attractions, hub constraints, and sourced sunset data. Use when ordering activities or creating a daily itinerary file.
---

# Draft Itinerary Day

Use this skill only within the Japan trip repository. This is a stage 5
procedure; ask before advancing to stage 5 or reopening a completed stage.
Read `AGENTS.md`, `workflow.md`, `schema.md`, root `constraints.md`, and the
hub's `constraints.md`.

## Procedure

1. Confirm the hub has a positive `nights` value and a valid `date_range`.
2. Confirm the date is inside the hub's half-open sleep interval
   `[start, end)`. Do not duplicate a checkout or transfer date.
3. Confirm the hub daylight table has a sourced sunset value for the date.
4. Copy `hubs/_template/itinerary/_day-template.md` to
   `hubs/<hub>/itinerary/YYYY-MM-DD.md`.
5. Fill frontmatter with the matching `date`, `hub`, and local `sunset` in
   `HH:MM`.
6. Link only selected attractions, using
   `../attractions/selected/<slug>.md`.
7. Order `daylight_sensitive: yes` activities before sunset. Account for
   travel time, duration, opening or booking constraints, meals, and breaks
   without inventing facts.
8. Before editing Markdown, run
   `python scripts/validate.py --references <path>`, inspect dependents, then
   run `python scripts/validate.py`.

Do not link inbox, shortlisted, or skipped attractions. Do not create itinerary
files for dates outside the hub's sleep interval.
