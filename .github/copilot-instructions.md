# Project Documentation Guidelines

## Documentation Map

Each feature is a file or subfolder directly under `docs/`. Only use a subfolder when a feature has child pages.

- Proxy service and routes: `docs/proxy-service/` (has child: unit-testing)
- Architecture and project structure: `docs/architecture.md`
- Configuration reference: `docs/configuration.md`
- Database schema and strategy: `docs/database.md`
- Deployment (Docker, Dokploy): `docs/deployment.md`
- Analytics dashboard: `docs/analytics.md`
- Request insight pipeline: `docs/request-insights.md`

## Monorepo Navigation

This repository uses a strict monorepo structure utilizing `uv workspaces` and VS Code Multi-root Workspaces.

1. ALWAYS identify the active package boundary before making code suggestions.
2. The codebase is broken down into `packages/` (shared libraries) and `services/` (deployed apps).
3. Do not modify files outside of the target package unless explicitly instructed to do so. Context should be scoped strictly to the package you are working on.
