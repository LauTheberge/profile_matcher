from dotenv import dotenv_values

from session import AsyncSessionManager

config = dotenv_values('.env')
postgres_url = config['DATABASE_URL']

# Create the session manager
session_manager = AsyncSessionManager(postgres_url)

async def get_db_session():
	async with session_manager.session() as session:
		yield session
