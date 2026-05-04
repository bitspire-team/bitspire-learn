import json
import logging

import pandas as pd
import streamlit as st
from src.data import load_messages
from tzlocal import get_localzone

logger = logging.getLogger(__name__)


def _render_message(text: str, meta_data: dict | str | None):
    if text and text.strip():
        st.markdown(text.strip())

    if not meta_data:
        return

    # Handle both stringified and loaded JSON formats
    if isinstance(meta_data, str):
        try:
            meta_data = json.loads(meta_data)
        except Exception:
            return

    if isinstance(meta_data, dict):
        for tag_name, xml_blocks in meta_data.items():
            with st.expander(f"XML Block: {tag_name}", expanded=False):
                if isinstance(xml_blocks, list):
                    for block in xml_blocks:
                        st.code(block, language="xml")
                else:
                    st.code(str(xml_blocks), language="xml")


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

    for _, row in interaction_df.iterrows():
        role = row.get("role", "user")
        text = str(row.get("text") or "")
        meta_data = row.get("meta_data")
        model = row.get("model")

        avatar = "🤖" if role == "assistant" else "🧾"

        with st.chat_message(role, avatar=avatar):
            caption = str(role).capitalize()
            if model:
                caption += f" ({model})"

            st.caption(caption)
            _render_message(text, meta_data)

logger.info("Successfully rendered the messages page.")
