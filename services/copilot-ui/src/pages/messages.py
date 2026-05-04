import json
import logging

import pandas as pd
import streamlit as st
from src.data import load_messages
from tzlocal import get_localzone

logger = logging.getLogger(__name__)


def _extract_generated_messages(response_body):
    if isinstance(response_body, str):
        try:
            response_body = json.loads(response_body)
        except Exception:
            return []
    if not isinstance(response_body, dict):
        return []

    generated_messages = []

    for choice in response_body.get("choices") or []:
        msg = choice.get("message") or {}
        if msg.get("content"):
            generated_messages.append(
                {"role": msg.get("role") or "assistant", "content": str(msg["content"])}
            )

    chunks, roles = {}, {}
    for event in response_body.get("sse_events") or []:
        for choice in event.get("choices") or []:
            idx = choice.get("index", 0)
            delta = choice.get("delta") or {}
            if delta.get("role"):
                roles[idx] = delta["role"]
            if delta.get("content"):
                chunks.setdefault(idx, []).append(str(delta["content"]))

    for idx, content_chunks in sorted(chunks.items()):
        content = "".join(content_chunks).strip()
        if content:
            generated_messages.append({"role": roles.get(idx, "assistant"), "content": content})

    return generated_messages


st.title("Messages")
df = load_messages()
if df.empty:
    st.info("No messages recorded yet.")
    st.stop()

df["created_on"] = pd.to_datetime(df["created_on"], utc=True).dt.tz_convert(get_localzone()).dt.tz_localize(None)
st.metric("Total Messages", len(df))

recent_interactions = df.groupby("interaction_id")["created_on"].max().sort_values(ascending=False)

interaction_options = []
for i_id in recent_interactions.index:
    if i_id:
        count = len(df[df["interaction_id"] == i_id])
        dt_str = recent_interactions[i_id].strftime("%Y-%m-%d %H:%M:%S")
        interaction_options.append(f"{dt_str} | {i_id} ({count} msgs)")

st.write("#### Conversations")
selected_option = st.selectbox("Select an interaction (chat turn)", interaction_options)

if selected_option:
    selected_i_id = selected_option.split(" | ")[1].split(" ")[0]
    st.write(f"**Interaction ID:** {selected_i_id}")

    interaction_df = df[df["interaction_id"] == selected_i_id]
    rendered_generated_for_requests = set()

    for _, row in interaction_df.iterrows():
        with st.chat_message("user", avatar="🧾"):
            st.caption("U")
            st.markdown(row["content"])

        request_log_id = row.get("request_log_id")
        if request_log_id not in rendered_generated_for_requests:
            generated_messages = _extract_generated_messages(row.get("response_body"))
            for generated in generated_messages:
                with st.chat_message("assistant", avatar="🤖"):
                    st.caption("Generated response")
                    st.markdown(generated["content"])

            if not generated_messages:
                with st.chat_message("assistant", avatar="🤖"):
                    st.info("No generated response was captured for this request.")
            rendered_generated_for_requests.add(request_log_id)

logger.info("Successfully rendered the messages page.")
