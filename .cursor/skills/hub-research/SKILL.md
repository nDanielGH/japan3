---
name: hub-research
description: Research and complete a Japan-trip hub with sourced local constraints, destination context, daylight data, and user-provided facts. Use when filling hub details.
disable-model-invocation: true
---

# Research hub

## Preconditions

- Require an existing active hub and read its README, `constraints.md`, and
  `research/` contents before editing.
- Read `AGENTS.md`, `hubs/AGENTS.md`, `schema.md`, and root `constraints.md`.
- Run `python scripts/validate.py --references <path>` for each existing or
  newly copied Markdown file to be edited.
- Follow the repository Mutation protocol. Declare the exact hub Markdown
  files owned by this operation and stop if any overlaps existing user
  changes.

## Allowed operation

1. Combine public web research with facts and preferences supplied by the user.
   Prefer official destination, attraction, and transport sources for
   operational claims; record conflicting sources as open questions instead
   of choosing silently.
2. Put hub-only rules, transit limits, check-in/out details, and sourced sunset
   tables in `hubs/<name>/constraints.md`. Sunset rows must use the documented
   inclusive date-range, local-time, and source-cell format.
3. Put broader destination findings in uniquely named
   `hubs/<name>/research/*.md` notes.
4. Cite factual claims as:
   `- <claim> — [<title>](URL) — accessed YYYY-MM-DD`.
5. Mark unresolved claims `UNVERIFIED` and add one matching unchecked question
   under `## Open questions`.
6. Preserve supported facts and ask before changing a user constraint.
7. Run `python scripts/validate.py` and the configured Markdown checks against
   every changed Markdown file. If any check fails, restore all owned paths
   from the pre-operation backup and report the failure.

Do not schedule nights, select attractions, or invent local rules, sunset data,
opening hours, or transit facts.
