import logging

import pandas as pd
import streamlit as st
from src.data import load_token_usages

logger = logging.getLogger(__name__)


class DataProcessor:
    @staticmethod
    def get_last_24_hours_usage(df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Filtering token usage for the past 24 hours.")
        if df.empty or "created_on" not in df.columns:
            return pd.DataFrame()

        now = pd.Timestamp.now(tz="UTC")
        twenty_four_hours_ago = now - pd.Timedelta(hours=24)

        df["created_on"] = pd.to_datetime(df["created_on"], utc=True)
        recent_df = df[df["created_on"] >= twenty_four_hours_ago].copy()

        if recent_df.empty:
            return pd.DataFrame()

        recent_df["hour"] = recent_df["created_on"].dt.floor("h")

        hourly = recent_df.groupby("hour")[["prompt_tokens", "completion_tokens"]].sum().reset_index()
        return hourly.set_index("hour")


st.title("Tokens")

df = load_token_usages()
if df.empty:
    st.info("No token usages recorded yet.")
    st.stop()

# 1. Numbers
total_tokens = df["total_tokens"].sum()
prompt_tokens = df["prompt_tokens"].sum()
completion_tokens = df["completion_tokens"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total Tokens", f"{total_tokens:,}")
col2.metric("Prompt Tokens", f"{prompt_tokens:,}")
col3.metric("Completion Tokens", f"{completion_tokens:,}")

# 2. Graph over 24 hours
st.write("#### Token Usage Over the Last 24 Hours")
recent_hourly_usage = DataProcessor.get_last_24_hours_usage(df)
if not recent_hourly_usage.empty:
    st.area_chart(recent_hourly_usage)
else:
    st.info("No token usage in the past 24 hours.")

# Grouped Metrics: tokens by user, repo, model
st.write("#### Token Counts")
col1, col2, col3 = st.columns(3)

with col1:
    st.write("##### By Model")
    model_counts = df.groupby("model")["total_tokens"].sum().reset_index()
    st.dataframe(model_counts, hide_index=True)

with col2:
    st.write("##### By User")
    user_counts = df.groupby("user_login")["total_tokens"].sum().reset_index()
    st.dataframe(user_counts, hide_index=True)

with col3:
    st.write("##### By Repository")
    repo_counts = df.groupby("repository_nwo")["total_tokens"].sum().reset_index()
    st.dataframe(repo_counts, hide_index=True)

# Average Cost: calculate and display average total_tokens per answer for each model.
st.write("#### Average Cost Per Model (Tokens per Answer)")
avg_cost = df.groupby("model")["total_tokens"].mean().reset_index()
avg_cost = avg_cost.rename(columns={"total_tokens": "avg_tokens"})
st.dataframe(avg_cost, hide_index=True)

# Conversation Breakdown: table grouped by interaction_id.
st.write("#### Conversation Breakdown")
conv_breakdown = (
    df.groupby("interaction_id")
    .agg(
        {
            "total_tokens": "sum",
            "prompt_tokens": "sum",
            "completion_tokens": "sum",
            "model": "first",
            "user_login": "first",
            "repository_nwo": "first",
        }
    )
    .reset_index()
)
st.dataframe(conv_breakdown, hide_index=True)

logger.info("Successfully rendered the tokens page.")
