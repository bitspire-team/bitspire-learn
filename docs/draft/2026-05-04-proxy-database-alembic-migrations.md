# Database Migrations: Switching to Alembic

## Context
When we added new columns (`text`, `meta_data`, `model`) to the `Message` table in the Copilot Proxy, we realized the project was using `Base.metadata.create_all()` in `src/core/db.py`. While sufficient for greenfield setups without data, SQLAlchemy's `create_all` does not issue `ALTER TABLE` commands for schemas that have evolved over time. This forced us to run raw SQL manually.

## Decision
We have added `alembic` to the dependencies in `pyproject.toml` and initialized an Async Alembic setup inside `services/copilot-proxy/alembic`. 

- Installed `alembic`.
- Initialized `alembic` using the async template (`alembic init -t async alembic`).
- Updated `env.py` to point `target_metadata` directly to our models (`src.core.db.Base.metadata`) and set the connection string using our loaded `settings.DATABASE_URL`.

## Why
Alembic is the standard tool for SQLAlchemy schema management. It maintains the version history of the database through python migration scripts (e.g. `alembic revision --autogenerate -m "description"`), ensuring that any developer checking out the codebase is able to run one command (`alembic upgrade head`) to get an up-to-date and consistent dev database. It natively handles adding columns, altering types, dropping tables, and maintaining indices.

## Next Steps
Because our development database is already instantiated and currently holds tables deleted from the model graph, generating an initial migration locally will output drops instead of creates. To properly baseline this, we should drop the local database, generate the initial `alembic revision`, check it in, and let Alembic completely replace `Base.metadata.create_all` going forward.

## Migration Execution (Best Practice)
For production deployments on Dokploy using Docker, the migrations should run automatically during container startup. 
- We added `alembic/` and `alembic.ini` to the production stage of the `Dockerfile`.
- We inlined the startup command within the `Dockerfile` using `CMD ["sh", "-c", "alembic upgrade head && exec python -m uvicorn src.main:app --host 0.0.0.0 --port 8080"]`.
- This ensures that whenever Dokploy rolls out a new Docker image containing schema changes, the database is upgraded before the application accepts traffic, avoiding the need for an external script file while maintaining the same reliability.