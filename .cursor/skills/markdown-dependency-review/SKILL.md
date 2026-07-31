---
name: markdown-dependency-review
description: Find and assess Markdown files affected by a planned repository edit, then validate the updated dependency set. Use when changing README, AGENTS, workflow, schema, constraints, templates, or other Markdown.
---

# Markdown Dependency Review

Use this skill before changing a Markdown file in the Japan trip repository.
The reference report is a discovery aid, not a complete semantic analysis.

## Procedure

1. Identify the target Markdown path relative to the repository root.
2. Run:
   `python scripts/validate.py --references <target>`
3. Read every referring file reported, including templates and `AGENTS.md`
   files.
4. Inspect semantic references as well as literal Markdown links:
   filenames, frontmatter fields, stage rules, validator assumptions, and
   procedures that mention the target.
5. Update all affected dependents consistently. Preserve canonical ownership:
   filesystem status, frontmatter metadata, root constraints, schema, and
   workflow rules must not be duplicated or silently overridden.
6. Run `python scripts/validate.py`.
7. If validation fails, fix the affected documents and repeat until it passes,
   or clearly report an intentionally stage-gated failure.

Use repository-relative paths with forward slashes in commands and skill
references.
