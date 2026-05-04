# Draft: UI Messages SSE Generated Response Parsing

**Date:** 2026-05-04

## Problem
Generated assistant responses were not visible in the Messages page even when grouped conversations were selected.

## Cause
Chat completion responses were stored in `response_logs.body.sse_events` as streamed delta chunks, but the UI extractor only read top-level `choices` and therefore missed streamed content.

## Decision
Parse both top-level `choices` and streamed `sse_events[].choices[].delta.content`, join delta chunks per choice index into full generated text, and render generated output in a distinct green highlighted block labeled "Generated response" to clearly separate it from logged request messages.