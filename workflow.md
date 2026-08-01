# Iterative planning workflow

Planning is a set of repeatable workstreams, not a single repository-wide
stage. Different hubs may be at different levels of readiness, and work may
return to an earlier workstream whenever new information changes the plan.

Run `python scripts/validate.py` after non-trivial edits. The validator checks
invariants continuously; it does not decide whether research is complete or
whether a planning decision is desirable.

## Workstreams

The project skills own repeatable file operations. This document describes
planning boundaries and dependencies; `AGENTS.md` and `schema.md` remain
authoritative for safety rules and invariants.

### Hub discovery and research

Use `hub-create`, `hub-research`, and `hub-reject` for candidate sleep bases.
A hub is ready for attraction or scheduling work when it has the required
structure and enough sourced local context. Research may continue while it
remains a candidate.

### Attraction research and triage

Use `attraction-create`, `attraction-research`, and `attraction-triage` for
ideas within one active hub. A record is ready for triage when its purpose,
logistics, duration, daylight, and booking context are sourced or its open
questions clearly describe what remains unknown.

Attractions intended for day planning belong in that hub's `selected/`
collection. Unresolved ideas may remain in `inbox/` or `shortlisted/` while
other work proceeds.

### Hub schedule

Use `hub-draft-schedule` for the higher-level route, such as “5 nights in
Tokyo, then 3 nights in Osaka.” It allocates sleep bases and date ranges, not
individual attractions or daily activities.

### Day itinerary

Use `hub-draft-day-itinerary` for one date within a scheduled hub. It creates
an ordered plan from that hub's selected attractions and sourced local sunset
data.

## Dependencies and iteration

The prerequisite is local to the artifact being edited:

```text
hub-create
  -> hub-research and attraction work for that hub
  -> attraction-triage to selected
  -> hub-draft-schedule
  -> hub-draft-day-itinerary
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

Mark a hub `complete` only after its full scheduled sleep interval has one
validated itinerary day per night. Until then, partial schedules and partial
itinerary plans are valid intermediate states.

Ask the user before making final attraction decisions, changing trip-wide
constraints, or treating the whole trip as complete. Detailed confirmation and
conflict rules live in the relevant project skill.
