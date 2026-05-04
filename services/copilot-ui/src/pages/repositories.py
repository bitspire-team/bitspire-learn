import logging

import pandas as pd
import streamlit as st
from src.data import load_repositories
from tzlocal import get_localzone

logger = logging.getLogger(__name__)
st.title("Repositories")
df = load_repositories()
if df.empty:
    st.info("No repositories recorded yet.")
    st.stop()
df["created_on"] = pd.to_datetime(df["created_on"], utc=True).dt.tz_convert(get_localzone()).dt.tz_localize(None)
st.metric("Total Repositories", len(df))
st.dataframe(df, use_container_width=True, hide_index=True)
logger.info("Successfully rendered the repositories page.")
