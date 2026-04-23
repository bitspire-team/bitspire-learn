# Proxy URL Construction Draft

- **Problem**: When constructing the `target_url` in the proxy route handler, the `TARGET_BASE_URL` included a scheme (`https://`), causing `request.url.replace(netloc=TARGET_BASE_URL)` to create an invalid URL like `https://https://...`.
- **Intention**: Correctly replace the domain/base of the incoming URL with the target base URL.
- **Requirements**: Maintain the path and query parameters while swapping the base part of the URL cleanly.
- **Criticality**: The target URL must be perfectly well-formed, or the upstream HTTP client will fail or make requests to incorrect endpoints.
- **Why**: Doing a string replacement `str(request.url).replace(str(request.base_url), f"{TARGET_BASE_URL}/")` simplifies the process and avoids `url.replace` scheme duplication issues.
- **Evolution**: Earlier attempts tried to use URL properties, but string replacement on the fully rendered URLs proved more robust when the replacement target already contains the scheme.