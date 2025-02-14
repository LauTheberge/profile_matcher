import asyncio

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, create_engine

from dotenv import dotenv_values

# Load the environment variables from the .env file
config = dotenv_values('.env')

# Fetch the database URL from the .env file

postgres_url = config['DATABASE_URL']

engine = create_async_engine(postgres_url)


async def init_db():
	async with engine.begin() as conn:
		# await conn.run_sync(SQLModel.metadata.drop_all)
		await conn.run_sync(SQLModel.metadata.create_all)

async def drop_db():
	async with engine.begin() as conn:
		await conn.run_sync(SQLModel.metadata.drop_all)