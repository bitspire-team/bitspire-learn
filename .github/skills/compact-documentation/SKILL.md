---
name: compact-documentation
description: 'Squash-merges drafts from docs/draft/ into finalized, up-to-date documentation under docs/features/. Removes stale content. Validates against actual implementation.'
---

# Compact Documentation

Compaction is the squash merge of the learning loop. Drafts are individual commits (dated changes). Compaction compresses them into a single, clean, up-to-date document per topic — the release.

## Purpose
Produce direct, concise, well-structured documentation that gives Copilot (and humans) a clear understanding of the topic. The compacted doc is the single source of truth. Drafts are consumed and deleted.

## When to Use
- Periodically after drafts accumulate in `docs/draft/`.
- When asked to organize, compact, or finalize documentation.
- When a feature or topic is complete.

## Procedure

### 1. Audit Drafts
- Read all files in `docs/draft/`. Drafts are dated (e.g., `2026-04-27-middleware-extraction.md`), so multiple drafts may exist for the same topic across different dates.
- For each draft, check whether the content still matches the actual implementation by reading the relevant source files.
- **Discard anything outdated or reversed.** If a later draft supersedes an earlier one on the same topic, only the latest state matters. The compacted doc reflects current reality, not history.

### 2. Group by Topic
- Identify which drafts belong to the same feature or topic, regardless of date.
- Multiple dated drafts compress into one feature doc (like commits squashing into a release).
- A single draft may also become its own feature doc if the topic is distinct enough.

### 3. Write the Compacted Doc
Place the result directly under `docs/` as `docs/<topic>.md`. Only use a subfolder (`docs/<topic>/index.md`) when the feature has child pages. Read the template before writing.

**GitHub Pages frontmatter:** Every feature doc must start with YAML frontmatter for the `just-the-docs` theme:
```yaml
---
title: <Topic Name>
nav_order: <next available number>
---
```
Check existing docs in `docs/` to determine the next `nav_order` value. The title appears in the sidebar navigation.

### 4. Move Technical Details to Code Comments
During compaction, identify technical details from drafts that do NOT belong in the feature doc but would be valuable as code comments. For each such detail:
- Read the relevant source file.
- If the detail is not already captured in a comment or test, **add a comment to the code** explaining the why.
- **Do not include the detail in the feature doc.** The feature doc should not repeat what the code already says (or now says, after you commented it).

Examples of details that belong in code, not docs:
- Why a specific parameter value was chosen (e.g., timeout, header list)
- Workarounds for framework quirks (e.g., closure factories for late binding, `request._receive` override)
- Why an alternative approach was rejected at that exact code location
- Edge case handling rationale

Examples of details that belong in docs, not code:
- Product-level "what it does" and "why it exists"
- Architecture and data flow diagrams
- Cross-cutting decisions that span multiple files
- Route tables, config tables, environment setup

The rule: if a detail is localized to one code location, it belongs as a comment there. If it spans the system, it belongs in the doc.

### 5. Quality Rules
- **Direct and concise.** No filler, no preamble, no "in this document we will...".
- **Assertive.** State what IS, not what was explored. Write "We use X because Y", not "After exploring A, B, C, we decided on X".
- **Implementation-accurate.** Every code snippet, path, and config value must match the current source. If it doesn't, fix it or remove it.
- **No duplication.** If two feature docs would say the same thing, consolidate.
- **Scannable.** Use headers, tables, and short paragraphs. A reader should find any fact in under 10 seconds.
- **Don't document what the code already says.** If a detail is obvious from the code, a comment, a variable name, or a test — skip it from the doc. Add a comment to the code if needed, then omit from the doc.

### 6. Clean Up
- Delete all draft files that were fully compacted into the feature doc.
- If a draft was only partially relevant (some content compacted, some still in progress), update the draft to remove the compacted portions and keep only what remains open.

## Assets
- **Template:** `.github/skills/compact-documentation/assets/feature-template.md`

## References
- **Draft input folder:** `docs/draft/`
- **Compacted output folder:** `docs/`
- **Draft skill:** `.github/skills/document-learning-draft/SKILL.md`