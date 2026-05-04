import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("postgresql+asyncpg://pi:xylMzkDEc901@raspberrypi:5432/development")


async def main():
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE messages ADD COLUMN text VARCHAR"))
            print("Added text")
        except Exception as e:
            print(e)
        try:
            await conn.execute(text("ALTER TABLE messages ADD COLUMN meta_data JSON"))
            print("Added meta_data")
        except Exception as e:
            print(e)
        try:
            await conn.execute(text("ALTER TABLE messages ADD COLUMN model VARCHAR"))
            print("Added model")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    asyncio.run(main())
