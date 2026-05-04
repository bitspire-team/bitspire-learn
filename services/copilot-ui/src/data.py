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
def load_routes():
    logger.info("Loading routes from the database.")
    query = text("SELECT id, method, path, created_on FROM routes ORDER BY created_on DESC")
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    logger.info("Loaded %d routes from the database.", len(df))
    return df


@st.cache_data(ttl=30)
def load_prompts():
    logger.info("Loading prompts from the database.")
    query = text("SELECT id, hash, role, content, created_on FROM prompts ORDER BY created_on DESC")
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    logger.info("Loaded %d prompts from the database.", len(df))
    return df


@st.cache_data(ttl=30)
def load_attachments():
    logger.info("Loading attachments from the database.")
    query = text("SELECT id, hash, type, content, created_on FROM attachments ORDER BY created_on DESC")
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    logger.info("Loaded %d attachments from the database.", len(df))
    return df


@st.cache_data(ttl=30)
def load_messages():
    logger.info("Loading messages from the database.")
    query = text("""
        SELECT
            m.id,
            m.request_log_id,
            m.role,
            m.content,
            m.text,
            m.meta_data,
            m.model,
            m.created_on,
            r.headers->>'x-interaction-id' as interaction_id,
            resp.timestamp as response_timestamp
        FROM messages m
        LEFT JOIN request_logs r ON m.request_log_id = r.id
        LEFT JOIN response_logs resp ON resp.request_id = m.request_log_id
        ORDER BY m.created_on ASC
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    df = df.where(pd.notna(df), None)
    logger.info("Loaded %d messages from the database.", len(df))
    return df
