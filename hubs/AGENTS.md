# Hub directory rules

Each direct child of `hubs/` except `_template/` and `graveyard/` is an active
sleep base; exclude both reserved directories from README Status `hubs:`.

## Hub operations

Use `hub-create`, `hub-research`, and `hub-reject` for repeatable hub
operations. Those skills own the procedures, confirmation boundaries, and
validation steps.

This file defines only local directory invariants: put hub metadata in its
README and local rules/sunset data in its `constraints.md`; do not create a
manual index or `hubs/README.md`.

## Hub contents

- `README.md` — metadata/context.
- `attractions/` — triaged attraction files.
- `constraints.md` — local rules and sourced sunsets.
- `itinerary/` — one `YYYY-MM-DD.md` per day.
- `research/` — sources and open questions.

Root `AGENTS.md` governs triage, research, hub schedules, day itineraries, and
validation. Work on each hub independently; another hub does not need to be at
the same readiness level.
