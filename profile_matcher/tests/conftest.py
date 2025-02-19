import asyncio
import os
import random
from typing import AsyncIterator, AsyncGenerator

import asyncpg
import pytest
import pytest_asyncio
from asyncpg import DuplicateDatabaseError
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from profile_matcher.database import get_db_session

load_dotenv()

os.environ['DATABASE_NAME'] = 'TechTestDatabase'
DATABASE_URL = os.environ['DATABASE_URL'] = (
    'postgresql+asyncpg://postgres:1234@127.0.0.1:5432/TestDatabase'
)
os.environ['DATABASE_USER'] = 'postgres'
os.environ['DATABASE_HOST'] = '127.0.0.1'
os.environ['DATABASE_PASSWORD'] = '1234'
os.environ['DATABASE_PORT'] = '5432'
os.environ['APP_PORT'] = '8000'
os.environ['APP_HOST'] = '127.0.0.1'

from main import app

TEST_DB_ID = ''.join(str(random.randint(0, 9)) for _ in range(5))
DB_NAME = f'{"TestDatabase"}_{TEST_DB_ID}'
MOCK_DB_URL = DATABASE_URL.replace('TestDatabase', DB_NAME)

ENGINE = create_async_engine(MOCK_DB_URL)


@pytest.fixture(scope='session')
def event_loop():
    return asyncio.get_event_loop()


@pytest_asyncio.fixture(scope='function')
async def async_session() -> AsyncIterator[AsyncSession]:
    session = async_sessionmaker(ENGINE, class_=AsyncSession, expire_on_commit=False)

    async with session() as session:
        async with ENGINE.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        yield session

    async with ENGINE.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await ENGINE.dispose()


@pytest_asyncio.fixture(scope='function')
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://testserver'
    ) as client:
        yield client


@pytest_asyncio.fixture(scope='function', autouse=True)
async def override_get_db_session(async_session):
    async def _get_test_db_session():
        yield async_session

    app.dependency_overrides[get_db_session] = _get_test_db_session
    yield
    app.dependency_overrides.clear()

    await ENGINE.dispose()


async def create_database_if_not_exists(database_url: URL, db_name: str):
    """Create the database if it does not exist."""
    asyncpg_url = f'postgres://{database_url.username}:{database_url.password}@{database_url.host}:{database_url.port}/postgres'
    conn = None
    try:
        conn = await asyncpg.connect(asyncpg_url)

        # Check if the database already exists
        existing_dbs = await conn.fetch('SELECT datname FROM pg_database')
        if db_name not in [db['datname'] for db in existing_dbs]:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f'Created database {db_name}')
        else:
            print(f'Database {db_name} already exists.')
    except DuplicateDatabaseError:
        print(f'Database {db_name} already exists.')
    except Exception as e:
        raise Exception('Failed to create test database: ' + str(e))
    finally:
        if conn:
            await conn.close()


async def wait_for_db_ready(
    database_url: URL, db_name: str, retries: int = 5, delay: int = 2
):
    """Wait for the database to be ready after creation."""
    asyncpg_url = f'postgres://{database_url.username}:{database_url.password}@{database_url.host}:{database_url.port}/{db_name}'
    for _ in range(retries):
        try:
            conn = await asyncpg.connect(asyncpg_url)
            await conn.close()
            print(f'Database {db_name} is ready.')
            return
        except Exception as e:
            print(f'Waiting for database {db_name} to be ready... {e}')
            await asyncio.sleep(delay)
    raise Exception(f'Database {db_name} is not ready after {retries} attempts.')


@pytest_asyncio.fixture(scope='session', autouse=True)
async def create_test_database_and_tables():
    parsed_url = ENGINE.url
    db_name = parsed_url.database

    await create_database_if_not_exists(parsed_url, db_name)

    # Ensure the database is ready before trying to create tables
    await wait_for_db_ready(parsed_url, db_name)

    async with ENGINE.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield ENGINE

    # Cleanup Phase: Terminate connections and drop the database
    await ENGINE.dispose()

    asyncpg_url = f'postgres://{parsed_url.username}:{parsed_url.password}@{parsed_url.host}:{parsed_url.port}/postgres'
    conn = await asyncpg.connect(asyncpg_url)
    try:
        await conn.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{db_name}' AND pid <> pg_backend_pid();
        """)
        await conn.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
    except Exception as e:
        raise Exception('Failed to drop test database: ' + str(e))
    finally:
        await conn.close()
