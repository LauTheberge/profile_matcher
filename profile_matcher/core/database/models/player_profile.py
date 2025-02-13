import uuid
from datetime import datetime, timezone
from typing import List, TypedDict

from pydantic import BaseModel, ConfigDict, Field as PydanticField
from pydantic.v1 import UUID4
from sqlmodel import SQLModel, Field


# Models for clan
class Clan(SQLModel, table=True):
    id: int = Field(default=None, description="Clan ID", primary_key=True)
    name: str = Field(default=None, description="Clan name")



# Models for player profile
class Inventory(BaseModel):

    # This model minimally defines the fields that are required for the Inventory mode (cash and coins), but allows for
    # any additional fields to be added
    __pydantic_extra__: dict[str, int] = PydanticField(init=False)
    cash: float = Field(default=0.0, description="Total amount of cash in player inventory")
    coins: int = Field(default=0, description="Total amount of coins in player inventory")
    model_config = ConfigDict(extra="allow")

class Device(BaseModel):
    id: int = Field(description="Device ID", primary_key=True)
    model: str = Field(description="Device model")
    carrier: str = Field(description="Carrier name")
    firmware: str = Field(description="Device firmware version")


class PlayerProfile(SQLModel, table=True):
    player_id: uuid.uuid4() = Field(description="Player ID", primary_key=True)
    credential: str = Field(description="Player credential")
    created: datetime = Field(default=datetime.now(tz=timezone.utc))
    modified: datetime = Field(default=datetime.now(tz=timezone.utc))
    last_session: datetime = Field(default=None, description="Last session when player logged in")
    total_spent: float = Field(default=0.0, description="Total amount of money spent by player")
    total_refund: float = Field(default=0.0, description="Total amount of money refunded to player")
    total_transactions: int = Field(default=0, description="Total number of transactions made by player")
    last_purchase: datetime = Field(default=None, description="Last purchase made by player")
    active_campaigns: List[str] = Field(default=None, description="List of active campaigns for player")
    devices: List[Device] = Field(description="List of devices used by player")
    level: int = Field(default=1, description="Player level")
    xp: int = Field(default=0, description="Player experience points for current level")
    total_playtime: int = Field(default=0, description="Total playtime in minutes")
    country: str = Field(description="Player country")
    language: str = Field(description="App language used by player")
    birthdate: datetime = Field(default=None, description="Player birthdate")
    gender: str = Field(default=None, description="Player gender")
    inventory: Inventory = Field(description="Player inventory")
    clan: Clan = Field(description="Player clan", foreign_key="clan.id")
    _custom_field: str = Field(default=None, description="Custom field for player profile")

#{
#  "player_id": "97983be2-98b7-11e7-90cf-082e5f28d836",
 # "credential": "apple_credential",
  #"created": "2021-01-10 13:37:17Z",
  #"modified": "2021-01-23 13:37:17Z",
  #"last_session": "2021-01-23 13:37:17Z",
  #"total_spent": 400,
  #"total_refund": 0,
  #"total_transactions": 5,
  #"last_purchase": "2021-01-22 13:37:17Z",
  #"active_campaigns": [],
  #"devices": [
  #  {
  #    "id": 1,
  #    "model": "apple iphone 11",
  #    "carrier": "vodafone",
  #    "firmware": "123"
  #  }
  #],
  #"level": 3,
  #"xp": 1000,
  #"total_playtime": 144,
  #"country": "CA",
  #"language": "fr",
  #"birthdate": "2000-01-10 13:37:17Z",
  #"gender": "male",
  #"inventory": {
  #  "cash": 123,
  #  "coins": 123,
  #  "item_1": 1,
  #  "item_34": 3,
  #  "item_55": 2
  #},
  #"clan": {
  #  "id": "123456",
  #  "name": "Hello world clan"
  #},
  #"_customfield": "mycustom"
#}

test_clan = Clan(id=123456, name="Hello world clan")

PlayerProfile(
    player_id="97983be2-98b7-11e7-90cf-082e5f28d836",
    credential="apple_credential",
    created=datetime(2021, 1, 10, 13, 37, 17, tzinfo=timezone.utc),
    modified=datetime(2021, 1, 23, 13, 37, 17, tzinfo=timezone.utc),
    last_session=datetime(2021, 1, 23, 13, 37, 17, tzinfo=timezone.utc),
    total_spent=400,
    total_refund=0,
    total_transactions=5,
    last_purchase=datetime(2021, 1, 22, 13, 37, 17, tzinfo=timezone.utc),
    active_campaigns=[],
    devices=[
        Device(id=1, model="apple iphone 11", carrier="vodafone", firmware="123")
    ],
    level=3,
    xp=1000,
    total_playtime=144,
    country="CA",
    language="fr",
    birthdate=datetime(2000, 1, 10, 13, 37, 17, tzinfo=timezone.utc),
    gender="male",
    inventory=Inventory(cash=123, coins=123, item_1=1, item_34=3, item_55=2),
    clan=test_clan,
    _custom_field="mycustom"
)


# This is for the test purpose (in order to seed the database with the test data)
# In a normal scenario, this data would be coming from the client application and the table would be created from
# a migration script