import logging
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
from src.data import load_requests
from tzlocal import get_localzone

logger = logging.getLogger(__name__)
st.title("Overview")
df = load_requests()
if df.empty:
    st.info("No requests recorded yet.")
    st.stop()

df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).dt.tz_convert(get_localzone()).dt.tz_localize(None)
df["success"] = df["status_code"].apply(lambda s: s < 400 if pd.notna(s) else False)

cutoff = datetime.now() - timedelta(hours=24)
df = df[df["timestamp"] >= cutoff]

if df.empty:
    st.info("No requests in the last 24 hours.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
total = len(df)
success_count = df["success"].sum()
failed_count = total - success_count
failure_rate = (failed_count / total * 100) if total > 0 else 0
col1.metric("Total Requests", total)
col2.metric("Successful", int(success_count))
col3.metric("Failed", int(failed_count))
col4.metric("Failure Rate", f"{failure_rate:.1f}%")

now = datetime.now().replace(minute=0, second=0, microsecond=0)
full_range = pd.date_range(start=now - timedelta(hours=23), end=now, freq="1h")
counts = df.set_index("timestamp").resample("1h")["success"]
chart_df = (
    pd.DataFrame(
        {
            "Successful": counts.sum(),
            "Failed": counts.count() - counts.sum(),
        }
    )
    .reindex(full_range, fill_value=0)
    .rename_axis("Timestamp")
)

st.write("#### Requests Over the Last 24 Hours")
st.area_chart(chart_df, color=["#2ecc71", "#e74c3c"], stack=True)

logger.info("Successfully rendered the overview page.")
