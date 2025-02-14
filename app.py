from contextlib import asynccontextmanager
from datetime import datetime, timezone

import asyncpg
import psycopg2
from fastapi import FastAPI
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from database import init_db, engine, drop_db
from profile_matcher.core.database.models import PlayerProfile, Clan, Device, Inventory


def get_session():
	with Session(engine) as session:
		yield session


async def create_data():
	"""
	Create data for testing purposes. In a real-world scenario, this data would come from the client.
	"""
	with AsyncSession(engine) as session:
		test_clan = Clan(
			id=123456,
			name='Hello world clan',
		)

		device = Device(
			id=1, model='apple iphone 11', carrier='vodafone', firmware='123'
		)
		inventory = Inventory(cash=123, coins=123, item_1=1, item_34=3, item_55=2)

		player_profile = PlayerProfile(
			player_id='97983be2-98b7-11e7-90cf-082e5f28d836',
			credential='apple_credential',
			created=datetime(2021, 1, 10, 13, 37, 17, tzinfo=timezone.utc),
			modified=datetime(2021, 1, 23, 13, 37, 17, tzinfo=timezone.utc),
			last_session=datetime(2021, 1, 23, 13, 37, 17, tzinfo=timezone.utc),
			total_spent=400,
			total_refund=0,
			total_transactions=5,
			last_purchase=datetime(2021, 1, 22, 13, 37, 17, tzinfo=timezone.utc),
			active_campaigns=[],
			devices=[device.model_dump()],
			level=3,
			xp=1000,
			total_playtime=144,
			country='CA',
			language='fr',
			birthdate=datetime(2000, 1, 10, 13, 37, 17, tzinfo=timezone.utc),
			gender='male',
			inventory=inventory.model_dump(),
			clan_id=test_clan.id,
			custom_field='mycustom',
		)
		await session.add(test_clan)
		await session.add(player_profile)
		await session.commit()
		await session.refresh(player_profile)


async def try_create_data():
	"""
	Try to create the data. If the data already exists, do nothing
	Once again, in a real-world scenario, this would not be present, as the data would be coming from the client.
	This is to prevent the program from trying to create the same data multiple times.
	"""
	with Session(engine) as session:
		statement_player = select(PlayerProfile)
		statement_clan = select(Clan)
		if (
			not session.exec(statement_player).first()
			and not session.exec(statement_clan).first()
		):
			await create_data()


# For the purpose of this test, we will use the asynccontextmanager decorator to create a lifespan event that will
# create the database and tables when the app starts and clear the metadata when the app stops.
@asynccontextmanager
async def lifespan(app: FastAPI):
	await init_db()
	await try_create_data()
	yield
	await drop_db()


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
