from contextlib import asynccontextmanager
from logging import Logger

import asyncpg
import uvicorn
from fastapi import FastAPI

from profile_matcher.api import client_config_router
from profile_matcher.data_creator import InitialDataCreator
from profile_matcher.database import session_manager

logger = Logger(__name__)


async def connect_to_db():
    return await asyncpg.connect(
        database='TestDatabase',
        user='postgres',
        host='127.0.0.1',
        password='1234',
        port=5432,
    )


# For purpose of this test, create a lifespan event that will
# create the database and tables when the app starts and clear the metadata when the app stops.
# In a normal scenario, table would be created from a migration script using Alembic.
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with session_manager.session() as db_session:
        connection = await connect_to_db()
        await session_manager.create_all()
        data_creator = InitialDataCreator()
        await data_creator.try_create_data(db_session)
        yield
        if session_manager.get_engine is not None:
            # Close the DB connection and clean up
            await session_manager.drop_all()
            await session_manager.close()
            await connection.close()


app = FastAPI(lifespan=lifespan)
app.include_router(client_config_router, tags=['client'])

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', log_level='debug', reload=True)
