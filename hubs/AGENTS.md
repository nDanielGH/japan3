# Hub directory rules

Each direct child of `hubs/` except `_template/` and `graveyard/` is an active
sleep base; exclude both reserved directories from README Status `hubs:`.

## Create a hub

1. Copy `_template/` to `hubs/<name>/` (unique kebab-case name).
2. Fill README frontmatter; keep `id` equal to `<name>`.
3. Add the folder name to the root README Status block.
4. Run `python scripts/validate.py`.

Put hub metadata in its README and local rules/sunset data in its
`constraints.md`; do not create a manual index or `hubs/README.md`.

## Reject a hub

Move rejected hubs intact to `hubs/graveyard/<name>/`; never delete or reuse
them. The location records rejection; add context to its README if needed.

## Hub contents

- `README.md` — metadata/context.
- `attractions/` — triaged attraction files.
- `constraints.md` — local rules and sourced sunsets.
- `itinerary/` — one `YYYY-MM-DD.md` per day.
- `research/` — sources and open questions.

Root `AGENTS.md` governs triage, research, itinerary, and validation.
