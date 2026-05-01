---
title: Monorepo Architecture
nav_order: 10
---

# Monorepo Architecture

## What It Does
Organizes the repository into a strict monorepo structure to support multiple independent packages and services. It enforces explicit boundaries for AI context, entangles dependencies correctly, and streamlines workspace navigation.

## Directory Structure

```text
bitspire-learn/
├── packages/           # Shared libraries (e.g., core utilities, shared models)
├── services/           # Deployed apps (e.g., copilot-proxy, copilot-ui)
└── pyproject.toml      # Root orchestration and global tools
```

## How It Works
- **`uv` Workspaces**: A single `.venv` manages all packages via the root `pyproject.toml` (configured with `[tool.uv.workspace]`), while keeping package definitions isolated.
- **VS Code Multi-Root Workspaces**: A `bitspire-learn.code-workspace` file assigns each package/service as a separate VS Code root folder, ensuring precise context isolation for Copilot and Pylance.
- **Global Tooling**: Linting and formatting configurations (`[tool.ruff]`) live globally in the root `pyproject.toml`.
- **Task Execution**: A single global `.vscode/tasks.json` defines commands, but every task explicitly scopes its execution boundary using the `"cwd"` property (mapping to `${workspaceFolder}/services/<service-name>`).

## Key Decisions

### Multi-Root Workspace for Context Isolation
**What:** Define packages and services as individual roots in `.code-workspace`.
**Why:** Creates explicit boundaries for Copilot's `WorkspaceContext` index and Pylance. Copilot isolates its suggestions and answers to the active package root, vastly improving AI accuracy.

### Local Directories Over Submodules
**What:** Store sub-packages as local directories in `packages/` and `services/`.
**Why:** Enables native indexing and search without the navigation disconnect of git submodules.

### Colocated Operational Files
**What:** Service-specific configurations (`Dockerfile`, `.dockerignore`) live inside their respective target bounds (`services/copilot-proxy/`), not at the repository root.
**Why:** Maintains a clean root focusing strictly on orchestration and generic documentation. Operational context stays with its relevant service.

### Global `tasks.json` with Scoped Contexts
**What:** Reusing one `.vscode/tasks.json` workspace-wide, with mandatory `cwd` targeting.
**Why:** Keeps task execution visible centrally in standard IDE views while guaranteeing paths/commands execute within bounded encapsulation limits.
