import contextlib
from logging import Logger
from typing import AsyncIterator

from dotenv import dotenv_values
from sqlalchemy.ext.asyncio import (
	create_async_engine,
	AsyncConnection,
	async_sessionmaker,
	AsyncEngine,
)
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

config = dotenv_values('.env')
postgres_url = config['DATABASE_URL']

class AsyncSessionManager:
	def __init__(self, postgres_url: str):
		self.__engine = create_async_engine(postgres_url)
		# We could also have two session makers, one for read and one for write. read_session_maker would
		# have autocommit=True
		self.__session_maker = async_sessionmaker(
			autocommit=False, bind=self.__engine, class_=AsyncSession
		)
		self.__loger = Logger('AsyncSessionManager')

	async def close(self):
		"""
		Close the database connection
		:raises Exception: If the connection is not initialized
		"""
		if self.__engine is None:
			raise Exception('DatabaseSessionManager is not initialized')
		await self.__engine.dispose()

		self.__engine = None
		self.__session_maker = None

	@contextlib.asynccontextmanager
	async def connect(self) -> AsyncIterator[AsyncConnection]:
		"""
		:raises Exception: If the connection is not initialized
		"""
		if self.__engine is None:
			raise Exception('DatabaseSessionManager is not initialized')

		async with self.__engine.begin() as connection:
			try:
				yield connection
			except Exception as e:
				await connection.rollback()
				self.__loger.error(f'Error in connection: {e}')
				raise e

	@contextlib.asynccontextmanager
	async def session(self) -> AsyncIterator[AsyncSession]:
		""" "
		:raises Exception: If the session maker is not initialized
		"""
		if self.__session_maker is None:
			raise Exception('DatabaseSessionManager is not initialized')

		session = self.__session_maker()
		try:
			yield session
		except Exception as e:
			await session.rollback()
			self.__loger.error(f'Error in session: {e}')
			raise e
		finally:
			await session.close()

	async def drop_all(self):
		"""
		For the purpose of testing, we can drop all tables in the database when the test is done in order to keep the
		database clean.
		"""
		async with self.__engine.begin() as conn:
			await conn.run_sync(SQLModel.metadata.drop_all)

	async def get_engine(self) -> AsyncIterator[AsyncEngine]:
		"""
		Return the engine
		"""
		yield self.__engine

	async def create_all(self):
		"""
		Create all tables in the database
		"""
		async with self.__engine.begin() as conn:
			await conn.run_sync(SQLModel.metadata.create_all)

# Create the session manager
session_manager = AsyncSessionManager(postgres_url)

async def get_db_session():
	async with session_manager.session() as session:
		yield session