from typing import Annotated


from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from profile_matcher.database import get_db_session


