import logging

import streamlit as st

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Copilot Proxy Dashboard", layout="wide")
st.markdown(
    "<style>.block-container { padding-top: 1rem; }</style>",
    unsafe_allow_html=True,
)

pg_overview = st.Page("pages/overview.py", title="Overview", url_path="overview", default=True)
pg_analytics = st.Page("pages/analytics.py", title="Analytics", url_path="analytics")
pg_requests = st.Page("pages/requests.py", title="Requests", url_path="requests")
pg_users = st.Page("pages/users.py", title="Users", url_path="users")
pg_repositories = st.Page("pages/repositories.py", title="Repositories", url_path="repositories")
pg_messages = st.Page("pages/messages.py", title="Messages", url_path="messages")

pg = st.navigation(
    {
        "Navigation": [pg_overview, pg_analytics, pg_requests],
        "Entities": [pg_users, pg_repositories, pg_messages],
    }
)
pg.run()
