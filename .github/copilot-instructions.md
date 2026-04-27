# Project Documentation Guidelines

## Documentation Map
Each feature is a file or subfolder directly under `docs/`. Only use a subfolder when a feature has child pages.

- Proxy service and routes: `docs/proxy-service/` (has child: unit-testing)
- Architecture and project structure: `docs/architecture.md`
- Configuration reference: `docs/configuration.md`
- Database schema and strategy: `docs/database.md`
- Deployment (Docker, Dokploy): `docs/deployment.md`
- Analytics dashboard: `docs/analytics.md`
- Self-improvement learning loop: `docs/self-improvement.md`
- Request insight pipeline: `docs/request-insights.md`

## Self-Improvement and Documentation Workflows
This repository enforces a strict "learn and document" methodology. Every preference, best practice, architectural decision, and feature detail must be documented so that the agent and team can learn and self-improve. 

Whenever you solve a problem, make a technical decision, or establish a new preference:
1. **MUST Execute `document-learning-draft`**: Use the `document-learning-draft` skill to immediately capture the problem, intention, requirements, what is critical, and *why* the decision was made. Store this draft under `docs/draft/`. Do not skip this step in conversations where meaningful decisions are made.
2. **MUST Execute `compact-documentation`**: Use the `compact-documentation` skill periodically, or when a feature/topic closes, to take drafts from `docs/draft/` and compact them into properly structured files under `docs/`.
3. **NEVER edit `docs/` directly.** All documentation changes must go through the draft process first. Only the `compact-documentation` skill writes to `docs/`.
4. Never skip this documentation step. Ensure every little detail—from small optimizations to large architectural choices—is captured in `docs/` for long-term memory and learning.
