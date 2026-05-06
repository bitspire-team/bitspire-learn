import logging

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from src.core.config import settings

logger = logging.getLogger(__name__)
engine = create_engine(settings.DATABASE_URL)


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
    logger.info("Loaded %d requests from the database.", len(df))
    return df


@st.cache_data(ttl=30)
def load_users():
    logger.info("Loading users from the database.")
    query = text("SELECT id, github_id, login, name, email, avatar_url, created_on FROM users ORDER BY created_on DESC")
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    logger.info("Loaded %d users from the database.", len(df))
    return df


@st.cache_data(ttl=30)
def load_repositories():
    logger.info("Loading repositories from the database.")
    query = text("SELECT id, owner, name, nwo, created_on FROM repositories ORDER BY created_on DESC")
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    logger.info("Loaded %d repositories from the database.", len(df))
    return df


@st.cache_data(ttl=30)
def load_messages():
    logger.info("Loading messages from the database.")
    query = text("""
        WITH latest_requests AS (
            SELECT DISTINCT ON (r.headers->>'x-interaction-id')
                r.id as request_id,
                r.headers->>'x-interaction-id' as interaction_id
            FROM request_logs r
            WHERE r.timestamp >= NOW() - INTERVAL '24 hours'
              AND r.headers->>'x-interaction-id' IS NOT NULL
            ORDER BY r.headers->>'x-interaction-id', r.timestamp DESC
        )
        SELECT
            m.id,
            m.request_log_id,
            m.role,
            m.content,
            m.text,
            m.meta_data,
            m.model,
            m.created_on,
            lr.interaction_id,
            resp.timestamp as response_timestamp
        FROM messages m
        INNER JOIN latest_requests lr ON m.request_log_id = lr.request_id
        LEFT JOIN response_logs resp ON resp.request_id = m.request_log_id
        ORDER BY m.created_on ASC
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    df = df.where(pd.notna(df), None)
    logger.info("Loaded %d messages from the database.", len(df))
    return df


@st.cache_data(ttl=30)
def load_token_usages():
    logger.info("Loading token usages from the database.")
    query = text("""
        SELECT
            tu.id,
            tu.interaction_id,
            tu.model,
            tu.prompt_tokens,
            tu.completion_tokens,
            tu.total_tokens,
            tu.created_on,
            u.login as user_login,
            r.nwo as repository_nwo
        FROM token_usages tu
        LEFT JOIN users u ON tu.user_id = u.id
        LEFT JOIN repositories r ON tu.repository_id = r.id
        ORDER BY tu.created_on DESC
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    logger.info("Loaded %d token usages from the database.", len(df))
    return df
