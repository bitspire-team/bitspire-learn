# Draft: UI Messages Generated Response Rendering

**Date:** 2026-05-04

## Problem
The Messages page only showed logged request messages, which made it difficult to inspect full conversation flow because generated assistant responses were missing.

## Cause
The data query for messages did not include linked response payloads from `response_logs`, and the page renderer only displayed rows from the `messages` table.

## Decision
Join `messages` to `response_logs` through `request_log_id` in `load_messages`, extract generated content from `response_body.choices[*].message` and `response_body.choices[*].delta`, and render generated entries inline as assistant chat messages with distinct visual treatment from logged input messages.