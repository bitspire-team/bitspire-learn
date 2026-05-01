# Draft: Separate Setup and Configuration for Copilot UI

**Date:** 2026-05-01

## Problem
The `copilot-ui` service was failing with `ModuleNotFoundError: No module named 'src.core'` because it tried to import from `src.core.config`, a module that only existed in the `copilot-proxy` service. 

## Cause
The UI service (`services/copilot-ui`) was built under the assumption that it would share or have access to the `copilot-proxy` backend's `src/core/config.py`. However, as a standalone process ran with Streamlit in its own directory, the shared `src/core` import path pointed to a non-existent package.

## Decision
Created a standalone `src/core/config.py` using `pydantic-settings` to manage environment variables specifically for the `copilot-ui` service. Additionally, a dedicated `.env` file was added in the `copilot-ui` directory. This decouples the UI service configuration from the proxy service and correctly establishes the `src.core` module for the UI app.