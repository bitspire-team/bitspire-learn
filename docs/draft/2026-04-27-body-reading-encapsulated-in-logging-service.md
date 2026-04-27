# Draft: Body Reading Encapsulated in LoggingService

**Date:** 2026-04-27

## Problem
Body-reading logic for requests and responses was scattered as module-level functions, separate from the class that used them.

## Cause
The functions were extracted for reuse but placed at module level by default, far from their only consumer.

## Decision
`read_request_body()`, `read_response_body()`, `parse_as_json()`, and `parse_as_sse()` are now `@staticmethod`s on `LoggingService`. Each encapsulates both the read and the reassignment hack (request._receive / response.body_iterator) so callers get a single clean call.
