from contextlib import asynccontextmanager

import psycopg2
from fastapi import FastAPI
from sqlmodel import Session, SQLModel, create_engine

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    SQLModel.metadata.clear()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Profile Matcher"}


conn = psycopg2.connect(database="TechTestDatabase",
                        user="postgres",
                        host='localhost',
                        password="1234",
                        port=5432)
