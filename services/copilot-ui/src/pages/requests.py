import streamlit as st
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
import re
from tzlocal import get_localzone
from src.data import load_requests

logger = logging.getLogger(__name__)
st.title("Requests")
df = load_requests()
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).dt.tz_convert(get_localzone()).dt.tz_localize(None)
df["status"] = df["status_code"].apply(lambda s: "🟢" if pd.notna(s) and s < 400 else "🔴")

with st.container(border=True):
    col1, col2 = st.columns([3, 1])
    min_date = df["timestamp"].min().date()
    max_date = df["timestamp"].max().date()
    with col1:
        date_range = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
    with col2:
        st.write("")
        st.write("")
        failed_only = st.toggle("Failed only", value=False)

filtered = df.copy()
if len(date_range) == 2:
    start = pd.Timestamp(date_range[0])
    end = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
    filtered = filtered[(filtered["timestamp"] >= start) & (filtered["timestamp"] < end)]
if failed_only:
    filtered = filtered[filtered["status"] == "🔴"]

display = filtered[["status", "timestamp", "method", "path", "status_code"]].copy()
display.columns = ["Status", "Timestamp", "Method", "Path", "Code"]
st.dataframe(display, use_container_width=True, hide_index=True)

failed = filtered[filtered["status"] == "🔴"].dropna(subset=["status_code"])
if not failed.empty:
    st.write("#### Error Details")
    failed["error_key"] = failed["response_body"].apply(
        lambda b: re.sub(r"[\w-]+/[\w.-]+", "<repo>", str(b)) if b else "No response body"
    )
    for error_key, group in failed.groupby("error_key", sort=False):
        sample = group.iloc[0]
        count = len(group)
        label = f"🔴 {sample['method']} {sample['path']} — {int(sample['status_code'])} ({count}x)"
        with st.expander(label):
            body = sample.get("response_body")
            if body:
                st.json(body)
            else:
                st.write("No response body recorded.")
            if count > 1:
                st.write(f"**Affected paths:** {', '.join(group['path'].unique())}")

success_count = filtered[filtered["status"] == "🟢"].shape[0]
rate = (success_count / len(filtered) * 100) if len(filtered) > 0 else 0
st.write(f"**{len(filtered)}** of **{len(df)}** requests — **{rate:.1f}%** success rate")

logger.info("Successfully rendered the requests page.")
