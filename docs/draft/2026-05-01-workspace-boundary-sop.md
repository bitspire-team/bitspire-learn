# Draft: Workspace Boundary SOP

**Date:** 2026-05-01

## Problem
Copilot and Pylance need proper boundary isolation and context for each package or service, but simply adding a folder inside a monorepo doesn't automatically isolate it properly within the IDE tools.

## Cause
VS Code uses the `.code-workspace` file to configure multi-root workspaces, which dictate root boundaries for tools like Pylance and Copilot. These tools cannot inherently infer sub-project boundaries just by their directory presence without explicit configuration. 

## Decision
Establish a Standard Operating Procedure (SOP): Whenever a new package is created inside `services/` or `packages/`, the developer must manually append its path to the `"folders"` array in `bitspire-learn.code-workspace` (or use *File > Add Folder to Workspace...*). This relies entirely on VS Code's local workspace boundaries, keeping our configuration Git-agnostic (i.e., no submodules needed) while instantly unlocking Copilot and Pylance boundary intelligence. Old references (like global `src/`) should also be routinely cleaned out.