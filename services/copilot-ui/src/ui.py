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
pg_requests = st.Page("pages/requests.py", title="Requests", url_path="requests")
pg_users = st.Page("pages/users.py", title="Users", url_path="users")
pg_repositories = st.Page("pages/repositories.py", title="Repositories", url_path="repositories")
pg_routes = st.Page("pages/routes.py", title="Routes", url_path="routes")
pg_prompts = st.Page("pages/prompts.py", title="Prompts", url_path="prompts")
pg_attachments = st.Page("pages/attachments.py", title="Attachments", url_path="attachments")
pg_messages = st.Page("pages/messages.py", title="Messages", url_path="messages")

pg = st.navigation(
    {
        "Navigation": [pg_overview, pg_requests],
        "Entities": [pg_users, pg_repositories, pg_routes, pg_prompts, pg_attachments, pg_messages],
    }
)
pg.run()
