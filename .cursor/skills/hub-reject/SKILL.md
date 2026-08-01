---
name: hub-reject
description: Reject a Japan-trip hub by preserving it in the graveyard with a user-provided reason. Use when removing a destination candidate from active planning.
disable-model-invocation: true
---

# Reject hub

## Preconditions

- Require the active hub name and a specific reason supplied by the user.
- Read `AGENTS.md`, `hubs/AGENTS.md`, `schema.md`, and the root README Status.
- Confirm the hub exists and is not `_template` or `graveyard`.
- Run `python scripts/validate.py --references hubs/<name>/README.md` and
  `--references README.md` before editing either Markdown file.
- Follow the repository Mutation protocol. The owned paths are the active hub
  directory, its proposed graveyard destination, and the root `README.md`;
  stop if any overlaps existing user changes.

## Confirmation boundary

Before moving anything, report the proposed source, destination, and reason:
`hubs/<name>/` → `hubs/graveyard/<name>/`. Require explicit user confirmation.

## Allowed operation after confirmation

1. Move the entire directory intact to `hubs/graveyard/<name>/`.
2. Add the rejection reason to the hub README without deleting research or
   context.
3. Remove the hub name from root README Status `hubs:` and update the dashboard.
4. Run `python scripts/validate.py` and the configured Markdown checks against
   every changed Markdown file. If any check fails, restore the active hub,
   graveyard destination, and dashboard from the pre-operation backup and
   report the failure.

Never delete a hub or overwrite an existing graveyard entry. Stop if the
destination exists or the reason is missing.
