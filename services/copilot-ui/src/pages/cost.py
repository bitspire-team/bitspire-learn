import logging

import pandas as pd
import streamlit as st
from src.core.config import settings
from src.data import load_token_usages

logger = logging.getLogger(__name__)


class CostEstimator:
    @staticmethod
    def calculate_costs(df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Computing token cost estimation.")
        cost_df = df.copy()
        prompt_rate = settings.PRICE_PER_1M_PROMPT_TOKENS / 1_000_000
        completion_rate = settings.PRICE_PER_1M_COMPLETION_TOKENS / 1_000_000

        # Replace NaN with 0 in case of missing data
        cost_df["prompt_tokens"] = cost_df["prompt_tokens"].fillna(0)
        cost_df["completion_tokens"] = cost_df["completion_tokens"].fillna(0)

        cost_df["estimated_prompt_cost"] = cost_df["prompt_tokens"] * prompt_rate
        cost_df["estimated_completion_cost"] = cost_df["completion_tokens"] * completion_rate
        cost_df["total_estimated_cost"] = cost_df["estimated_prompt_cost"] + cost_df["estimated_completion_cost"]
        logger.info("Token cost estimation completed.")
        return cost_df

    @staticmethod
    def get_last_24_hours_cost(df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Filtering token costs for the past 24 hours.")
        if df.empty or "created_on" not in df.columns:
            return pd.DataFrame()

        now = pd.Timestamp.now(tz="UTC")
        twenty_four_hours_ago = now - pd.Timedelta(hours=24)

        df["created_on"] = pd.to_datetime(df["created_on"], utc=True)
        recent_df = df[df["created_on"] >= twenty_four_hours_ago].copy()

        if recent_df.empty:
            return pd.DataFrame()

        recent_df["hour"] = recent_df["created_on"].dt.floor("h")

        hourly = recent_df.groupby("hour")[["estimated_prompt_cost", "estimated_completion_cost"]].sum().reset_index()
        return hourly.set_index("hour")


def main():
    st.title("Cost")

    df = load_token_usages()
    if df.empty:
        st.info("No token usages recorded yet, cannot estimate cost.")
        st.stop()

    cost_df = CostEstimator.calculate_costs(df)

    total_prompt = cost_df["estimated_prompt_cost"].sum()
    total_completion = cost_df["estimated_completion_cost"].sum()
    total_overall = cost_df["total_estimated_cost"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Prompt Cost", f"${total_prompt:,.4f}")
    col2.metric("Total Completion Cost", f"${total_completion:,.4f}")
    col3.metric("Overall Estimated Cost", f"${total_overall:,.4f}")

    # 24-Hour Window Chart
    st.write("#### Cost Over the Last 24 Hours")
    recent_hourly_cost = CostEstimator.get_last_24_hours_cost(cost_df)
    if not recent_hourly_cost.empty:
        st.area_chart(recent_hourly_cost)
    else:
        st.info("No cost incurred in the past 24 hours.")

    st.write("### Cost Breakdown by Model")
    model_costs = (
        cost_df.groupby("model")[["estimated_prompt_cost", "estimated_completion_cost", "total_estimated_cost"]]
        .sum()
        .reset_index()
    )
    st.dataframe(model_costs, use_container_width=True)

    st.write("### Cost Tracker")
    st.dataframe(
        cost_df[["created_on", "user_login", "model", "prompt_tokens", "completion_tokens", "total_estimated_cost"]],
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
