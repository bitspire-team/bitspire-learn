# Draft: Simplify Message.id from Composite String to Integer

**Date:** 2026-05-04

## Problem
The Message model used a composite String ID (e.g., `"{request_log_id}_req_{i}"` and `"{request_log_id}_res_{i}"`) constructed by concatenating the parent `request_log_id` with a role suffix and index. This was unnecessarily complex since the `request_log_id` foreign key already provides the parent-child relationship.

## Cause
The composite ID pattern was originally designed to encode the relationship between messages and request logs directly in the primary key. However, this duplicates information already captured by the `request_log_id` foreign key column. Other derived/static entity models in the codebase (users, routes, prompts, repositories, attachments) already use simple Integer auto-increment PKs.

## Decision
Changed `Message.id` from `String` to `Integer` with auto-increment, consistent with the reference pattern used by other static entity models (e.g., `User.id`).

### Changes Made
1. **`services/copilot-proxy/src/models/message.py`**: Changed `id = Column(String, primary_key=True, index=True)` → `id = Column(Integer, primary_key=True, index=True)`
2. **`services/copilot-proxy/src/services/request_insight.py`**: Removed `id=f"{request_log_id}_req_{i}"` and `id=f"{request_log_id}_res_{i}"` parameters from both `resolve_messages()` and `resolve_generated_messages()` create calls. The repository's `create()` method now omits the `id` parameter, letting the database auto-generate it.
3. **`services/copilot-proxy/alembic/versions/dc54357fb2b2_simplify_message_id_to_integer.py`**: Created Alembic migration that:
   - Creates `messages_id_seq` sequence
   - Adds new `id_new INTEGER` column with sequence default
   - Drops old VARCHAR `id` column and renames `id_new` to `id`
   - Recreates primary key constraint and index

### Impact Assessment
- Grep confirmed NO code parses the composite ID to derive `request_log_id` — only the two creation sites in `request_insight.py` constructed the composite IDs
- Tests directory has no message ID pattern dependencies
- All 6 existing tests pass after the change

### Key Insight
When a foreign key already establishes a parent-child relationship, the child's primary key does not need to encode that relationship. Simple auto-increment Integer PKs are sufficient and consistent with the rest of the codebase.
