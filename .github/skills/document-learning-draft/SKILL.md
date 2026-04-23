---
name: document-learning-draft
description: 'Use whenever a critical decision is made, a problem is solved, or learning occurs during a conversation. Identifies what is critical, why the decision was made, the problem, intention, and requirements. Saves thoughts to docs/draft/.'
---

# Document Learning Draft

## When to Use
- A new architectural or technical decision is made.
- A problem is identified and solved.
- We establish a new preference, best practice, or feature detail.
- You are explicitly asked to document learnings or thoughts.

## Procedure
1. Analyze the recent conversation to identify:
   - **Problem**: What was the issue or challenge?
   - **Intention**: What was the goal of the solution?
   - **Requirements**: What constraints or requirements had to be met?
   - **Criticality**: What is the most critical part of this decision?
   - **Why**: Why was this specific decision or approach chosen?
   - **Evolution**: How did the decision or requirement change during the conversation?
2. Format these insights as structured markdown.
3. Save the document to `docs/draft/<topic-name>-draft.md`. Create the directory if it doesn't exist. If the document already exists, **append and update it** rather than overwriting it, so we can trace the decision-making process over time.
4. Ensure the draft is updated continuously (e.g., after each response where new decisions or clarifications emerge) to maintain an accurate timeline of the learning process.
