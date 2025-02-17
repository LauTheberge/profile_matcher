import contextlib
import os
from logging import Logger
from typing import AsyncIterator

import asyncpg
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncConnection,
    async_sessionmaker,
    AsyncEngine,
)
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from ._exception import AsyncSessionManagerException

load_dotenv()  # This will load the .env variables
POSTGRES_URL = os.getenv('DATABASE_URL')


class AsyncSessionManager:
    def __init__(self):
        self.__engine = create_async_engine(POSTGRES_URL)
        # We could also have two session makers, one for read and one for write. read_session_maker would
        # have autocommit=True
        self.__session_maker = async_sessionmaker(
            autocommit=False, bind=self.__engine, class_=AsyncSession
        )
        self.__loger = Logger('AsyncSessionManager')

    async def create_database_if_not_exists(self):
        """
        Ensure the database exists before creating tables.
        """
        parsed_url = self.__engine.url
        db_name = parsed_url.database

        # Convert SQLAlchemy-style DSN to asyncpg-compatible DSN
        asyncpg_url = f'postgres://{parsed_url.username}:{parsed_url.password}@{parsed_url.host}:{parsed_url.port}/postgres'

        conn = await asyncpg.connect(asyncpg_url)
        try:
            db_exists = await conn.fetchval(
                'SELECT 1 FROM pg_database WHERE datname=$1', db_name
            )
            if not db_exists:
                await conn.execute(f'CREATE DATABASE "{db_name}"')
        finally:
            await conn.close()  # Manually close the connection

    async def close(self):
        """
        Close the database connection
        :raises AsyncSessionManagerException: If the connection is not initialized
        """
        if self.__engine is None:
            raise AsyncSessionManagerException(
                'DatabaseSessionManager is not initialized'
            )
        await self.__engine.dispose()

        self.__engine = None
        self.__session_maker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """
        :raises AsyncSessionManagerException: If the connection is not initialized or there is an error in the connection
        """
        if self.__engine is None:
            raise AsyncSessionManagerException(
                'DatabaseSessionManager is not initialized'
            )

        async with self.__engine.begin() as connection:
            try:
                yield connection
            except AsyncSessionManagerException as e:
                await connection.rollback()
                self.__loger.error(f'Error in connection: {e}')
                raise e

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """ "
        :raises AsyncSessionManagerException: If the session maker is not initialized or there is an error in the session
        """
        if self.__session_maker is None:
            raise AsyncSessionManagerException(
                'DatabaseSessionManager is not initialized'
            )

        session = self.__session_maker()
        try:
            yield session
        except AsyncSessionManagerException as e:
            await session.rollback()
            self.__loger.error(f'Error in session: {e}')
            raise e
        finally:
            await session.close()

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
session_manager = AsyncSessionManager()


async def get_db_session():
    async with session_manager.session() as session:
        yield session
