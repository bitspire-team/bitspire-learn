# UI Messages: Moving Normalization to the Proxy

## Context
The Copilot UI used to reconstruct Server-Sent Events (SSE) payload into readable assistant messages on the fly. It was also manually extracting XML blocks (like `<skills>`) for each chat turn. We determined that this logic belongs to the Proxy, which intercepts the lifecycle of messages anyway.

## Decision
We moved all message parsing into the proxy level via `RequestInsightService`:
- Added `text` (String), `meta_data` (JSON), and `model` (String) columns to the `Message` model.
- Added `extract_xml_metadata` and `parse_content_payload` helpers to `request_insight.py` in the proxy package.
- Removed on-the-fly SSE buffering and regex XML filtering from `services/copilot-ui/src/pages/messages.py`.
- Replaced it with a cleaned-up UI loop that simply renders `message.text` and loops through `message.meta_data` for blocks.

## Why
Keeping the UI simple separates concerns properly. Since the text payload and XML tags are now fully parsed at the proxy level on-intercept and directly available in the database, the UI does not have to deal with computationally heavy regex operations on each refresh or try to map API logic like SSE packets into plain text. This also gives us access to specific XML events via database querying in the future.