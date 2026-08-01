---
name: hub-draft-schedule
description: Draft or revise the high-level Japan-trip hub calendar with hub order, date ranges, and nights. Use when allocating the trip window among sleep bases.
disable-model-invocation: true
---

# Draft hub schedule

## Preconditions

- Read root `constraints.md`, all active hub READMEs, `workflow.md`, and
  `schema.md`.
- Check `hubs/graveyard/` before considering a hub.
- Identify which hubs are candidates, active, or already scheduled.
- Run `python scripts/validate.py --references <hub-readme>` for every hub
  README that may change, and for `README.md` before changing the dashboard.

## Allowed operation

1. Propose an ordered sequence of hubs and explain the route logic and
   high-level transfers.
2. Assign each proposed hub a non-overlapping half-open `[start, end)` range
   inside the canonical trip window.
3. Set `nights` equal to the date difference and update the hub README
   frontmatter; set both fields together.
4. Preserve unscheduled hubs as `nights: null` and `date_range: null`.
5. Update the root README Status dashboard when the active scheduled set or
   next actions change.
6. Run `python scripts/validate.py`. If validation fails, stop and report the
   conflict; do not leave a partially updated schedule or dashboard.

This operation schedules sleep bases only. Do not assign attractions or create
day files. If the user has not approved a route or night allocation, present
the proposal and ask before editing.
