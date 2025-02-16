from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class Level(BaseModel):
    min: int
    max: int

class MatcherContent(BaseModel):
    country: Optional[list[str]] = None
    items: Optional[list[str]] = None

class Matcher(BaseModel):
    level: Level
    has: MatcherContent
    does_not_have: MatcherContent

class ActiveCampaign(BaseModel):
    game: str
    name: str
    priority: float
    matchers: Matcher
    start_date: datetime
    end_date: datetime
    enabled: bool
    last_updated: datetime


