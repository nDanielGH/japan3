---
name: attraction-research
description: Research and complete a Japan-trip attraction record using public sources and user-provided facts. Use when filling logistics, duration, daylight, booking, or decision context.
---

# Research attraction

## Preconditions

- Require one existing attraction record and read its hub rules, current
  frontmatter, and related research notes.
- Run `python scripts/validate.py --references <attraction-file>` before
  editing Markdown.
- Run the same reference audit for each research note that will be edited or
  created.

## Allowed operation

1. Combine public web research with facts and preferences supplied by the user.
   Prefer official attraction, operator, and transport sources for hours,
   access, booking, and closure claims; record conflicting sources as open
   questions instead of choosing silently.
2. Update the attraction with purpose, activity, logistics, duration, daylight
   sensitivity, booking requirements, and open questions.
3. Put factual claims and citations in hub `research/` notes, using:
   `- <claim> — [<title>](URL) — accessed YYYY-MM-DD`.
4. Mark unresolved claims `UNVERIFIED` and add a matching unchecked question.
5. If `booking_required: yes`, record a known `book_by` deadline or add an
   explicit question when it is unknown.
6. Preserve the current triage folder and `skip_reason` semantics.
7. Run `python scripts/validate.py`. If validation fails, stop and report the
   failure rather than leaving a partially rewritten record or research note.

Do not select or skip the attraction, invent facts, or treat an unverified
claim as established.
