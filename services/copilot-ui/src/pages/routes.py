import streamlit as st
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
import re
from tzlocal import get_localzone
from src.data import load_routes

logger = logging.getLogger(__name__)
st.title("Routes")
df = load_routes()
if df.empty:
    st.info("No routes recorded yet.")
    st.stop()
df["created_on"] = pd.to_datetime(df["created_on"], utc=True).dt.tz_convert(get_localzone()).dt.tz_localize(None)
st.metric("Total Routes", len(df))
st.dataframe(df, use_container_width=True, hide_index=True)
logger.info("Successfully rendered the routes page.")
