# UI Messages: Dynamic XML Block Rendering

## Context
When displaying messages in the Streamlit UI, we noticed that XML blocks like `<skills>`, `<agents>`, and `<attachment>` were being rendered inline, which could lead to poorly formatted or visually cluttered output.

## Decision
We implemented a dynamic regex-based parsing function `_render_message_content()` in `services/copilot-ui/src/pages/messages.py`. 

- **Regex**: `r'(?si)(<([a-z0-9_\-]+)[^>]*>.*?</\2>)'`
- It splits the content to extract all top-level XML-like elements and their tag names.
- Regular text is rendered normally using `st.markdown()`.
- XML tags are captured and displayed inside `st.expander(f"XML Block: {tag_name}", expanded=False)` using `st.code()` with XML highlighting.
- This applies to both user prompts and assistant generated responses because we replaced `st.markdown(content_text)` with `_render_message_content(content_text)` for both roles.

## Why
Dynamic matching avoids hardcoding specific XML blocks like `<skills>`. It separates the technical context from conversational output without cluttering the UI, making it easier to read the actual message contents while keeping the technical blocks accessible through expanders.
