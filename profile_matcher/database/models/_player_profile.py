from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from sqlmodel import SQLModel, Field, Relationship


# Models for clan
class Clan(SQLModel, table=True):
    id: int = Field(default=None, description='Clan ID', primary_key=True)
    name: str = Field(default=None, description='Clan name')

    players: List['PlayerProfile'] = Relationship(
        back_populates='clan', sa_relationship_kwargs={'lazy': 'selectin'}
    )


# Models for player profile
class PlayerProfile(SQLModel, table=True):
    __tablename__ = 'player-profile'
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
        sa_column=Column(ARRAY(String)),
        default=None,
        description='List of active campaigns for player',
    )
    level: int = Field(default=1, description='Player level')
    xp: int = Field(default=0, description='Player experience points for current level')
    total_playtime: int = Field(default=0, description='Total playtime in minutes')
    country: str = Field(description='Player country')
    language: str = Field(description='App language used by player')
    birthdate: datetime = Field(description='Player birthdate')
    gender: str = Field(description='Player gender')
    clan_id: int = Field(description='Player clan id', foreign_key='clan.id')
    custom_field: Optional[str] = Field(
        default=None, description='Custom field for player profile'
    )
    inventory: 'Inventory' = Relationship(
        back_populates='player', sa_relationship_kwargs={'lazy': 'selectin'}
    )
    devices: list['Device'] = Relationship(
        back_populates='player', sa_relationship_kwargs={'lazy': 'selectin'}
    )
    clan: 'Clan' = Relationship(
        back_populates='players', sa_relationship_kwargs={'lazy': 'selectin'}
    )


# Usually, Inventory would be a separate table containing with all the possible items and the number of each item
# that the player has. For the test purpose, it is kept as a JSONB field in the PlayerProfile table
# a one-to-one relations
class Inventory(SQLModel, table=True):
    id: int = Field(
        default=None, description='Inventory ID linked to a player', primary_key=True
    )
    player_id: str = Field(
        default=None,
        description='Player ID linked to the inventory',
        foreign_key='player-profile.player_id',
    )
    cash: float = Field(
        default=0.0, description='Total amount of cash in player inventory'
    )
    coins: int = Field(
        default=0, description='Total amount of coins in player inventory'
    )
    item_1: Optional[int] = Field(description='Number of item 1 in player inventory')
    item_4: Optional[int] = Field(description='Number of item 4 in player inventory')
    item_34: Optional[int] = Field(description='Number of item 34 in player inventory')
    item_55: Optional[int] = Field(description='Number of item 55 in player inventory')
    item_100: Optional[int] = Field(
        description='Number of item 100 in player inventory'
    )

    player: PlayerProfile = Relationship(
        back_populates='inventory', sa_relationship_kwargs={'lazy': 'selectin'}
    )


class Device(SQLModel, table=True):
    id: int = Field(description='Device ID', primary_key=True)
    player_id: str = Field(
        description='Player ID linked to the device',
        foreign_key='player-profile.player_id',
    )
    model: str = Field(description='Device model')
    carrier: str = Field(description='Carrier name')
    firmware: str = Field(description='Device firmware version')

    player: PlayerProfile = Relationship(
        back_populates='devices', sa_relationship_kwargs={'lazy': 'selectin'}
    )
