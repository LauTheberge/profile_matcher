from datetime import datetime, timezone
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field as PydanticField
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

from sqlmodel import SQLModel, Field


# Models for clan
class Clan(SQLModel, table=True):
	id: int = Field(default=None, description='Clan ID', primary_key=True)
	name: str = Field(default=None, description='Clan name')


# Models for player profile
class Inventory(BaseModel):
	# This model minimally defines the fields that are required for the Inventory mode (cash and coins), but allows for
	# any additional fields to be added
	__pydantic_extra__: dict[str, int] = PydanticField(init=False)
	cash: float = Field(
		default=0.0, description='Total amount of cash in player inventory'
	)
	coins: int = Field(
		default=0, description='Total amount of coins in player inventory'
	)
	model_config = ConfigDict(extra='allow')


class Device(SQLModel, table=False):
	id: int = Field(description='Device ID', primary_key=True)
	model: str = Field(description='Device model')
	carrier: str = Field(description='Carrier name')
	firmware: str = Field(description='Device firmware version')


class PlayerProfile(SQLModel, table=True):
	player_id: str = Field(
		description='Player ID', primary_key=True
	)  # This should be a uuid, but for the test purpose, it is set as a string
	credential: str = Field(description='Player credential')
	# Usually would have a default value of datetime.now(timezone.utc), but for the test purpose, it is set as None
	created: datetime
	# Usually would have a default value of datetime.now(timezone.utc), but for the test purpose, it is set as None
	modified: datetime
	last_session: Optional[datetime] = Field(
		default=None, description='Last session when player logged in'
	)
	total_spent: float = Field(
		default=0.0, description='Total amount of money spent by player'
	)
	total_refund: float = Field(
		default=0.0, description='Total amount of money refunded to player'
	)
	total_transactions: int = Field(
		default=0, description='Total number of transactions made by player'
	)
	last_purchase: Optional[datetime] = Field(
		default=None, description='Last purchase made by player'
	)
	active_campaigns: Optional[List[str]] = Field(
		sa_column=Column(
			ARRAY(String)),
			default=None,
			description='List of active campaigns for player',
		)
	devices: List[Device] = Field(
		sa_column=Column(JSONB),
		default_factory=list,
		description='List of devices used by player',
	)
	level: int = Field(default=1, description='Player level')
	xp: int = Field(default=0, description='Player experience points for current level')
	total_playtime: int = Field(default=0, description='Total playtime in minutes')
	country: str = Field(description='Player country')
	language: str = Field(description='App language used by player')
	birthdate: datetime = Field(description='Player birthdate')
	gender: Optional[str] = Field(default=None, description='Player gender')
	inventory: Inventory = Field(sa_column=Column(JSONB), description='Player inventory')
	clan_id: int = Field(description='Player clan id', foreign_key='clan.id')
	custom_field: Optional[str] = Field(
		default=None, description='Custom field for player profile'
	)


# This is for the test purpose (in order to seed the database with the test data)
# In a normal scenario, this data would be coming from the client application and the table would be created from
# a migration script using Alembic.
