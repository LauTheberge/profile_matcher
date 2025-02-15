from contextlib import asynccontextmanager
from logging import Logger

import asyncpg
import uvicorn
from dotenv import dotenv_values
from fastapi import FastAPI

from profile_matcher.data_creator import InitialDataCreator
from profile_matcher.session import AsyncSessionManager

# Load the environment variables from the .env file
config = dotenv_values('.env')
postgres_url = config['DATABASE_URL']


logger = Logger(__name__)

# Create the session manager
session_manager = AsyncSessionManager(postgres_url)


async def get_db_session():
	async with session_manager.session() as session:
		yield session


# For purpose of this test, create a lifespan event that will
# create the database and tables when the app starts and clear the metadata when the app stops.
@asynccontextmanager
async def lifespan(app: FastAPI):
	async with session_manager.session() as db_session:
		await session_manager.create_all()
		data_creator = InitialDataCreator()
		await data_creator.try_create_data(db_session)
		yield
		if session_manager.get_engine is not None:
			# Close the DB connection and clean up
			await session_manager.drop_all()
			await session_manager.close()


app = FastAPI(lifespan=lifespan)


@app.get('/')
async def root():
	return {'message': 'Profile Matcher'}


conn = asyncpg.connect(
	database='TestDatabase',
	user='postgres',
	host='127.0.0.1',
	password='1234',
	port=5432,
)


if __name__ == '__main__':
	uvicorn.run(app, host='0.0.0.0', log_level='debug')
