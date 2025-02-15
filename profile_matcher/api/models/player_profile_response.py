from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


# Models for clan
class Clan(BaseModel):
    id: int
    name: str


# Models for player profile
class Inventory(BaseModel):
    cash: int
    coins: int
    item_1: Optional[int]
    item_4: Optional[int]
    item_34: Optional[int]
    item_55: Optional[int]
    item_100: Optional[int]


class Device(BaseModel):
    id: int
    model: str
    carrier: str
    firmware: str

class PlayerProfileResponse(BaseModel):
    player_id: str
    credential: str
    created: datetime
    modified: datetime
    last_session: datetime
    total_spent: float
    total_refund: float
    total_transactions: int
    last_purchase: Optional[datetime]
    active_campaigns: list[str]
    devices: list[Device]
    level: int
    xp: int
    total_playtime: int
    country: str
    language: str
    birthdate: datetime
    gender: str
    inventory: Inventory
    clan: Clan
    custom_field: str

