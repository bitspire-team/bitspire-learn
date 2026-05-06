import logging

import pandas as pd
import streamlit as st
from src.data import load_token_usages

logger = logging.getLogger(__name__)

st.title("Token Usage Analytics")

df = load_token_usages()
if df.empty:
    st.info("No token usages recorded yet.")
    st.stop()

# Trend Chart: daily tokens line chart.
st.write("#### Daily Token Usage")
df["created_on_date"] = pd.to_datetime(df["created_on"]).dt.date
daily_tokens = df.groupby("created_on_date")["total_tokens"].sum().reset_index()
st.line_chart(daily_tokens.set_index("created_on_date"))

# Grouped Metrics: tokens by user, repo, model
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
conv_breakdown = df.groupby("interaction_id").agg({
    "total_tokens": "sum",
    "prompt_tokens": "sum",
    "completion_tokens": "sum",
    "model": "first",
    "user_login": "first",
    "repository_nwo": "first",
}).reset_index()
st.dataframe(conv_breakdown, hide_index=True)

logger.info("Successfully rendered the analytics page.")
