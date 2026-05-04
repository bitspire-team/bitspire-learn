# Draft: UI Messages Remove Unused Normalization

**Date:** 2026-05-04

## Problem
The messages page still contained a normalization helper and an unused import after switching message rendering to Markdown output.

## Cause
The earlier rendering approach used JSON normalization for code-block display, but the helper remained after moving to direct Markdown rendering.

## Decision
Removed the unused `_normalize_content` function and the unused `html` import, and replaced the remaining helper call in generated-message extraction with `str(msg["content"])` so content is always rendered as text without normalization.
