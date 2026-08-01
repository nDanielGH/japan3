# Iterative planning workflow

Planning is a set of repeatable workstreams, not a single repository-wide
stage. Different hubs may be at different levels of readiness, and work may
return to an earlier workstream whenever new information changes the plan.

Run `python scripts/validate.py` after non-trivial edits. The validator checks
invariants continuously; it does not decide whether research is complete or
whether a planning decision is desirable.

## Workstreams

### Hub discovery and research

- Copy `hubs/_template/` to `hubs/<name>/` for each candidate sleep base.
- Record local rules and sourced daylight data in the hub's `constraints.md`.
- Add broader destination research notes to the hub's `research/` collection.
- A rejected hub is moved intact to `hubs/graveyard/`.

**Ready for use:** the hub has valid required directories and enough sourced
context to evaluate attractions or scheduling. A hub can remain a candidate
while research continues.

### Attraction research

- Add one file per idea to the hub's `attractions/inbox/`.
- Record sourced claims in research notes and unresolved claims as open
  questions.
- Research may happen for any active hub at any time.

**Ready for triage:** the attraction has enough sourced purpose, logistics,
duration, daylight, and booking information to make a recommendation, or its
open questions clearly explain what remains unknown.

### Attraction triage

- Review each hub's attraction collections independently.
- Move records between `inbox/`, `shortlisted/`, `selected/`, and `skipped/`.
- Ask the user before every final move to `selected/` or `skipped/`.
- Keep rejected ideas in `skipped/` with a specific `skip_reason`.

**Ready for day planning:** the attractions intended for the itinerary are in
that hub's `selected/` collection. Unresolved attractions can remain in
`inbox/` or `shortlisted/` while other work proceeds.

### Hub schedule

The hub schedule is the higher-level trip route: for example, “5 nights in
Tokyo, then 3 nights in Osaka.” It is not a daily itinerary.

- Record a hub's `nights` and half-open `date_range` in its `README.md`.
- A hub schedule may be drafted before other hubs are scheduled.
- Ranges must stay within the canonical trip window and must not overlap.
- When all active hubs are scheduled, ranges must be contiguous and cover the
  full trip window.

**Ready for day planning:** the target hub has a valid schedule and sourced
local sunset data for the date being drafted.

### Day itinerary

- Create one `YYYY-MM-DD.md` in a hub's `itinerary/` for each planned day,
  starting from `_day-template.md`.
- A day belongs to exactly one hub and must fall within that hub's half-open
  sleep interval.
- Link only selected attractions from that same hub.
- Put daylight-sensitive activities before the sourced local sunset.

**Ready for trip completion:** every scheduled sleep night has a day file with
an ordered plan, valid selected-attraction links, and a local sunset.

## Dependencies and iteration

The prerequisite is local to the artifact being edited:

```text
hub exists
  -> attraction/research work for that hub
  -> selected attractions for that hub
  -> hub schedule for that hub
  -> dated day itineraries for that hub
```

The arrows do not impose a repository-wide order. For example, Tokyo can have
selected attractions and drafted day itineraries while Osaka is still being
researched. New research may reopen triage, scheduling, or day planning for
only the affected hub.

## Completion

There is no permanent “current stage.” The trip is complete when:

1. all intended hubs have valid, non-overlapping schedules covering the
   canonical trip window;
2. every attraction decision is resolved or explicitly deferred; and
3. every scheduled sleep night has a valid day itinerary.

Ask the user before making final attraction decisions, changing trip-wide
constraints, or treating the whole trip as complete.
