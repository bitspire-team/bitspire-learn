import logging

import pandas as pd
import streamlit as st
from src.data import load_prompts
from tzlocal import get_localzone

logger = logging.getLogger(__name__)
st.title("Prompts")
df = load_prompts()
if df.empty:
    st.info("No prompts recorded yet.")
    st.stop()
df["created_on"] = pd.to_datetime(df["created_on"], utc=True).dt.tz_convert(get_localzone()).dt.tz_localize(None)
df["preview"] = df["content"].str[:120] + df["content"].apply(lambda c: "..." if len(str(c)) > 120 else "")
st.metric("Total Prompts", len(df))
display = df[["id", "hash", "role", "preview", "created_on"]].copy()
display.columns = ["ID", "Hash", "Role", "Content Preview", "Created On"]
st.dataframe(display, use_container_width=True, hide_index=True)

st.write("#### Prompt Detail")
prompt_id = st.selectbox("Select a prompt to view full content", df["id"].tolist())
if prompt_id:
    row = df[df["id"] == prompt_id].iloc[0]
    st.write(f"**Role:** {row['role']}")
    st.code(row["content"], language="markdown")
logger.info("Successfully rendered the prompts page.")
