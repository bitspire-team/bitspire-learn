import streamlit as st
import pandas as pd
import glob
from pathlib import Path
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Requests Dashboard", layout="wide")
st.title("Requests Dashboard")


@st.cache_data
def load_data():
    logger.info("Starting to load request JSON files in bulk.")

    files = sorted(Path("requests").glob("*.json"))
    data = [json.loads(f.read_text(encoding="utf-8")) for f in files]
    df = pd.json_normalize(data)

    logger.info(f"Successfully loaded {len(data)} request files.")
    return df


df = load_data()

st.write("### All Requests")
for chat_id, group_df in df.groupby("request.headers.x-agent-task-id"):
    last_request = group_df.iloc[-1]
    model = last_request.get("request.body.model", "N/A")
    st.write(f"**Chat ID:** `{chat_id}`")
    st.badge(model)

    messages = last_request.get("request.body.messages", [])
    if isinstance(messages, list):
        st.dataframe(pd.json_normalize(messages))
    else:
        st.write("No messages found in the last request.")

logger.info("Successfully rendered the requests list on the dashboard.")
