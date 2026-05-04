import logging

import pandas as pd
import streamlit as st
from src.data import load_attachments
from tzlocal import get_localzone

logger = logging.getLogger(__name__)
st.title("Attachments")
df = load_attachments()
if df.empty:
    st.info("No attachments recorded yet.")
    st.stop()
df["created_on"] = pd.to_datetime(df["created_on"], utc=True).dt.tz_convert(get_localzone()).dt.tz_localize(None)
df["preview"] = df["content"].str[:120] + df["content"].apply(lambda c: "..." if len(str(c)) > 120 else "")
st.metric("Total Attachments", len(df))
display = df[["id", "hash", "type", "preview", "created_on"]].copy()
display.columns = ["ID", "Hash", "Type", "Content Preview", "Created On"]
st.dataframe(display, use_container_width=True, hide_index=True)

st.write("#### Attachment Detail")
attachment_id = st.selectbox("Select an attachment to view full content", df["id"].tolist())
if attachment_id:
    row = df[df["id"] == attachment_id].iloc[0]
    st.write(f"**Type:** {row['type']}")
    st.code(row["content"], language="markdown")
logger.info("Successfully rendered the attachments page.")
