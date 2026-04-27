---
name: document-learning-draft
description: 'Use whenever a problem is solved or a critical decision is made. Each draft is a commit in the learning loop — dated, single-topic, and tied to a specific change.'
---

# Document Learning Draft

Drafts are individual commits in a self-learning loop. Each draft captures one change, one problem, one decision — dated so the learning timeline is preserved. Compaction (the other skill) is the squash merge that compresses drafts into clean, current documentation.

## When to Use
- A problem is identified and solved.
- A critical technical or architectural decision is made.
- A meaningful code change is made that others (or Copilot) should learn from.

## Rules
- **Never edit `docs/` directly.** All documentation changes must start as a draft in `docs/draft/`. Only the `compact-documentation` skill is allowed to write to `docs/`. This is the single most important rule.
- **One change per file.** Each draft covers exactly one topic or decision.
- **File naming:** `docs/draft/YYYY-MM-DD-<topic>.md`. Date prefix uses the current date. Lowercase kebab-case for the topic.
- **New change, new file.** Even if a topic was drafted before, a new change gets a new dated file. This preserves the timeline. Compaction will merge them later.
- **Be direct.** State the problem, cause, and decision. No filler.

## Structure
Every draft must follow the template exactly. Read the template before writing.

## Assets
- **Template:** `.github/skills/document-learning-draft/assets/draft-template.md`

## References
- **Draft output folder:** `docs/draft/`
- **Compacted docs (final destination):** `docs/features/`
- **Compaction skill:** `.github/skills/compact-documentation/SKILL.md`

## What NOT to Include
- Approaches that were explored and rejected (unless the rejection reason is itself the learning).
- Conversation history or verbose exploration narratives.
- Requirements or intentions that are obvious from the decision itself.
