import streamlit as st
import pandas as pd
import logging
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from src.core.config import settings

import re
from tzlocal import get_localzone

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Requests Dashboard", layout="wide")
st.markdown(
    "<style>.block-container { padding-top: 1rem; }</style>",
    unsafe_allow_html=True,
)

sync_url = settings.DATABASE_URL.replace("+asyncpg", "+psycopg2")
engine = create_engine(sync_url)

if "page" not in st.session_state:
    st.session_state.page = "Overview"

st.sidebar.write("Navigation")
st.sidebar.button(
    "Overview",
    use_container_width=True,
    type="tertiary",
    on_click=lambda: st.session_state.update(page="Overview"),
)
st.sidebar.button(
    "Requests",
    use_container_width=True,
    type="tertiary",
    on_click=lambda: st.session_state.update(page="Requests"),
)
page = st.session_state.page


@st.cache_data(ttl=30)
def load_requests():
    logger.info("Loading requests from the database.")
    query = text("""
        SELECT req.id, req.timestamp, req.method, req.path, req.url,
               resp.status_code, resp.body as response_body
        FROM request_logs req
        LEFT JOIN response_logs resp ON resp.request_id = req.id
        ORDER BY req.timestamp DESC
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    logger.info(f"Loaded {len(df)} requests from the database.")
    return df


def render_overview_page():
    st.title("Overview")
    df = load_requests()
    if df.empty:
        st.info("No requests recorded yet.")
        return

    df["timestamp"] = (
        pd.to_datetime(df["timestamp"], utc=True)
        .dt.tz_convert(get_localzone())
        .dt.tz_localize(None)
    )
    df["success"] = df["status_code"].apply(lambda s: s < 400 if pd.notna(s) else False)

    cutoff = datetime.now() - timedelta(hours=24)
    df = df[df["timestamp"] >= cutoff]

    if df.empty:
        st.info("No requests in the last 24 hours.")
        return

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


def render_requests_page():
    st.title("Requests")
    df = load_requests()
    df["timestamp"] = (
        pd.to_datetime(df["timestamp"], utc=True)
        .dt.tz_convert(get_localzone())
        .dt.tz_localize(None)
    )
    df["status"] = df["status_code"].apply(
        lambda s: "🟢" if pd.notna(s) and s < 400 else "🔴"
    )

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
        filtered = filtered[
            (filtered["timestamp"] >= start) & (filtered["timestamp"] < end)
        ]
    if failed_only:
        filtered = filtered[filtered["status"] == "🔴"]

    display = filtered[["status", "timestamp", "method", "path", "status_code"]].copy()
    display.columns = ["Status", "Timestamp", "Method", "Path", "Code"]
    st.dataframe(display, use_container_width=True, hide_index=True)

    failed = filtered[filtered["status"] == "🔴"].dropna(subset=["status_code"])
    if not failed.empty:
        st.write("#### Error Details")
        failed["error_key"] = failed["response_body"].apply(
            lambda b: (
                re.sub(r"[\w-]+/[\w.-]+", "<repo>", str(b)) if b else "No response body"
            )
        )
        for error_key, group in failed.groupby("error_key", sort=False):
            sample = group.iloc[0]
            count = len(group)
            label = (
                f"🔴 {sample['method']} {sample['path']} — "
                f"{int(sample['status_code'])} ({count}x)"
            )
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
    st.write(
        f"**{len(filtered)}** of **{len(df)}** requests — **{rate:.1f}%** success rate"
    )

    logger.info("Successfully rendered the requests page.")


if page == "Overview":
    render_overview_page()
elif page == "Requests":
    render_requests_page()
