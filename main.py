import logging.config
import os
import pathlib
from contextlib import asynccontextmanager

import asyncpg
import uvicorn
from dotenv import dotenv_values, load_dotenv
from fastapi import FastAPI

from profile_matcher.api import client_config_router
from profile_matcher.data_creator import InitialDataCreator
from profile_matcher.database import session_manager


load_dotenv()
POSTGRES_URL = os.getenv('DATABASE_URL')

async def connect_to_db():
    return await asyncpg.connect(
        database=os.getenv('DATABASE_NAME'),
        user=os.getenv('DATABASE_USER'),
        host=os.getenv('DATABASE_HOST'),
        password=os.getenv('DATABASE_PASSWORD'),
        port=os.getenv('DATABASE_PORT'),
    )


# For purpose of this test, create a lifespan event that will
# create the database and tables when the app starts and clear the metadata when the app stops.
# In a normal scenario, table would be created from a migration script using Alembic.
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with session_manager.session() as db_session:
        await session_manager.create_database_if_not_exists()
        connection = await connect_to_db()
        await session_manager.create_all()
        data_creator = InitialDataCreator()
        await data_creator.try_create_data(db_session)
        yield
        if session_manager.get_engine is not None:
            # Close the DB connection
            await session_manager.close()
            await connection.close()


app = FastAPI(lifespan=lifespan)
app.include_router(client_config_router, tags=['client'])

log_config = str(pathlib.Path(__file__).parent / 'log.ini')
logging.config.fileConfig(log_config, disable_existing_loggers=False)

if __name__ == '__main__':
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=int(os.getenv('APP_PORT')),
        log_level='debug',
        log_config=log_config,
    )
