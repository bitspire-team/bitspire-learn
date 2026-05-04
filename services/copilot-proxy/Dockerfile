# ===== STAGE 1: Base =====
FROM python:3.12-slim AS base
WORKDIR /app

# Install uv and base dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache -r pyproject.toml

# ===== STAGE 2: Test =====
FROM base AS test

# Install test dependencies
RUN uv pip install --system --no-cache -e ".[test]"

# Copy source and tests
COPY src/ /app/src/
COPY tests/ /app/tests/

# Set env for tests
ENV DATABASE_URL="sqlite+aiosqlite:///:memory:"

# Run tests and create a marker file to enforce the test stage
RUN python -m pytest tests/ -v && touch /tests-passed

# ===== STAGE 3: Production =====
FROM base AS production

# Enforce that tests must pass before building production
COPY --from=test /tests-passed /tests-passed

# Copy application source code and migrations
COPY src/ /app/src/
COPY alembic/ /app/alembic/
COPY alembic.ini /app/alembic.ini

EXPOSE 8080

CMD ["sh", "-c", "alembic upgrade head && exec python -m uvicorn src.main:app --host 0.0.0.0 --port 8080"]
