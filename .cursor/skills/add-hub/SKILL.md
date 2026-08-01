---
name: add-hub
description: Create and validate a candidate Japan trip sleep-base hub from the repository template. Use when adding a hub, sleep base, or destination candidate.
---

# Add Hub

Use this skill only within the Japan trip repository. The repository's
`AGENTS.md`, `hubs/AGENTS.md`, `workflow.md`, `schema.md`, and
`constraints.md` remain authoritative.

## Procedure

1. Check the root README dashboard and choose this workstream when a new or
   existing candidate hub needs attention; unrelated hubs may be further ahead.
2. Check `hubs/graveyard/` for a rejected hub with the same or equivalent name.
3. Choose a unique lowercase kebab-case folder name.
4. Copy `hubs/_template/` to `hubs/<name>/`.
5. Fill `hubs/<name>/README.md` frontmatter:
   - `id` equal to the folder name
   - `name`, `base_location`, and any known context
   - keep `nights` and `date_range` as `null` until the hub schedule is drafted
   - keep `status: candidate` unless the repository workflow says otherwise
6. Add the folder name to the root README Status `hubs:` list. This dashboard
   tracks active folders; it does not assign a global workflow stage.
7. Before editing Markdown dependents, run:
   `python scripts/validate.py --references README.md`
8. Run `python scripts/validate.py`.

Do not create `hubs/README.md`, a manual hub index, or hub-specific trip dates
as part of hub creation. Date scheduling belongs to the separate hub schedule
workstream and may be done independently for each hub.
