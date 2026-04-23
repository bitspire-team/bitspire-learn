# Project Documentation Guidelines

## Self-Improvement and Documentation Workflows
This repository enforces a strict "learn and document" methodology. Every preference, best practice, architectural decision, and feature detail must be documented so that the agent and team can learn and self-improve. 

Whenever you solve a problem, make a technical decision, or establish a new preference:
1. **MUST Execute `document-learning-draft`**: Use the `document-learning-draft` skill to immediately capture the problem, intention, requirements, what is critical, and *why* the decision was made. Store this draft under `docs/draft/`. Do not skip this step in conversations where meaningful decisions are made.
2. **MUST Execute `compact-documentation`**: Use the `compact-documentation` skill periodically, or when a feature/topic closes, to take drafts from `docs/draft/` and compact them into properly structured files under `docs/features/`.
3. Never skip this documentation step. Ensure every little detail—from small optimizations to large architectural choices—is captured in `docs/` for long-term memory and learning.
