---
name: hub-create
description: Create a candidate Japan-trip hub from the repository template. Use when adding a sleep base or destination candidate to the trip repository.
disable-model-invocation: true
---

# Create hub candidate

## Preconditions

- Read `AGENTS.md`, `hubs/AGENTS.md`, `schema.md`, and `constraints.md`.
- Check `hubs/graveyard/` for a previously rejected hub with the same identity.
- Confirm the requested name is unique, lowercase kebab-case, and is not `_template` or `graveyard`.
- Follow the repository Mutation protocol. The owned paths are the new
  `hubs/<name>/` directory and the root `README.md`; stop if either overlaps
  existing user changes.

## Allowed operation

1. Copy `hubs/_template/` to `hubs/<name>/`.
2. Run `python scripts/validate.py --references hubs/<name>/README.md` before
   editing the new hub README, and run it for `README.md` before updating the
   root dashboard.
3. Fill only the known hub identity fields in `hubs/<name>/README.md`:
   `id`, `name`, `base_location`, and optional notes.
4. Keep `nights` and `date_range` as `null` unless the user explicitly asks to
   schedule the hub.
5. Add `<name>` to the root README Status `hubs:` list and update its focus,
   next actions, and date.
6. Run `python scripts/validate.py` and the configured Markdown checks against
   every changed Markdown file. If any check fails, restore the owned paths
   from the pre-operation backup and report the failure.

Do not invent local rules, sunset data, attractions, schedules, or research.
Do not edit `hubs/_template/`. If the name already exists, stop and report it.
