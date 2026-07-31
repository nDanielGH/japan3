# Hub directory rules

Each direct child of `hubs/` other than `_template/` and `graveyard/` is an
active sleep base. Those two reserved directories are not active hubs and
must not be included in the root README Status `hubs:` list.

## Create a hub

1. Copy `_template/` to `hubs/<name>/`, using a unique kebab-case name.
2. Fill the hub's `README.md` frontmatter and keep its `id` equal to `<name>`.
3. Add the folder name to the root README Status block.
4. Run `python scripts/validate.py`.

Hub metadata belongs in the hub README. Hub-specific rules and sunset data
belong in `constraints.md` inside that hub. Do not duplicate hub metadata in a
manually maintained index or a `hubs/README.md` file.

## Reject a hub

Move a rejected hub directory intact to `hubs/graveyard/<name>/`. Do not delete
it or reuse its name for a different hub. The directory's location records the
rejection; add a note to its README when the reason needs more context.

## Hub contents

- `README.md` — hub metadata and hub-specific context.
- `attractions/` — attraction files, with status encoded by folder.
- `constraints.md` — local rules and sourced sunset table.
- `itinerary/` — one `YYYY-MM-DD.md` file per day at this hub.
- `research/` — source notes and open questions.

The root `AGENTS.md` is authoritative for triage, research, itinerary, and
validation rules.
