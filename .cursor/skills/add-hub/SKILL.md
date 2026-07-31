---
name: add-hub
description: Create and validate a candidate Japan trip sleep-base hub from the repository template. Use when adding a hub, sleep base, or destination candidate.
---

# Add Hub

Use this skill only within the Japan trip repository. The repository's
`AGENTS.md`, `hubs/AGENTS.md`, `workflow.md`, `schema.md`, and
`constraints.md` remain authoritative.

## Procedure

1. Check the current stage in root `README.md`; ask before jumping ahead or
   reopening a finished stage.
2. Check `hubs/graveyard/` for a rejected hub with the same or equivalent name.
3. Choose a unique lowercase kebab-case folder name.
4. Copy `hubs/_template/` to `hubs/<name>/`.
5. Fill `hubs/<name>/README.md` frontmatter:
   - `id` equal to the folder name
   - `name`, `base_location`, and any known context
   - keep `nights` and `date_range` as `null` until stage 4
   - keep `status: candidate` unless the repository workflow says otherwise
6. Add the folder name to the root README Status `hubs:` list.
7. Before editing Markdown dependents, run:
   `python scripts/validate.py --references README.md`
8. Run `python scripts/validate.py`.

Do not create `hubs/README.md`, a manual hub index, or hub-specific trip dates.
