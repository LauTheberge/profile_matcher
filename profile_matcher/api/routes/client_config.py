from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from profile_matcher.api.models.player_profile_response import Inventory, Device
from profile_matcher.database import get_db_session
from profile_matcher.database.models import PlayerProfile, Clan

router = APIRouter()


@router.get(
    '/user/{player_id}'
)
async def get_user(player_id: str, session: AsyncSession = Depends(get_db_session)):
    """
    Get the user profile for a given player_id
    """
    statement = select(PlayerProfile).where(PlayerProfile.player_id == player_id)
    result = await session.exec(statement)
    player = result.first()

    return player


@router.get('/get_client_config/{player_id}', response_model=PlayerProfile)
async def get_client_config(player_id: int):
    pass


# This would usually be in a separate file with the first path of the route for all routes in the folder (for example,
# if we had more routes) with a separate router at the base path. for profile_matcher.
# | - route
# |     |---- client
# |             |------- get.py
# |             |------- post.py
# |             |------- put.py
#               ...
# |             |------- router.py
# |    |----- match
# |             |------- get.py
# |             |------- post.py
# |             |------- put.py
#               ...
# |             |------- router.py
# |    |----- router.py
#
# This is kept in the same file for simplicity, since we only have one route in this project, and the path of the
# route is straightforward.
