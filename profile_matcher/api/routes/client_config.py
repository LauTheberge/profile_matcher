from datetime import datetime
from logging import Logger

from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from werkzeug.exceptions import NotFound

from profile_matcher.api.models.campaign import (
    ActiveCampaign,
    Matcher,
    Level,
    MatcherContent,
)
from profile_matcher.api.models.player_profile_response import PlayerProfileResponse
from profile_matcher.database import get_db_session
from profile_matcher.database.models import PlayerProfile

router = APIRouter()


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


@router.get('/get_client_config/{player_id}', response_model=PlayerProfileResponse)
async def get_client_config(
    player_id: str, session: AsyncSession = Depends(get_db_session)
):
    """
    Return the player profile with the active campaign added
    """
    logger = Logger('Get_client_config')
    statement = select(PlayerProfile).where(PlayerProfile.player_id == player_id)
    result = await session.exec(statement)
    player = result.first()
    if player is None:
        logger.debug(f'No player found with id {player_id}')
        raise NotFound('No player found')

    # Commit to avoid idle in transaction before (mocked) external call
    await session.commit()

    active_sessions: list[ActiveCampaign] = mock_campaign_api()

    return player


def mock_campaign_api() -> list[ActiveCampaign]:
    """
    This mock an external api call to get all the active campaigns
    """
    campaign_level = Level(min=1, max=1)
    has_content = MatcherContent(country=['US', 'RO', 'CA'], items=['item_1'])
    does_not_have_content = MatcherContent(items=['item_4'])
    campaign_matchers = Matcher(
        level=campaign_level, has=has_content, does_not_have=does_not_have_content
    )
    campaign = ActiveCampaign(
        game='mygame',
        name='mycampaign',
        priority=10.5,
        matchers=campaign_matchers,
        start_date=datetime(2022, 1, 25),
        end_date=datetime(2022, 2, 25),
        enabled=True,
        last_updated=datetime(2021, 7, 13),
    )
    return [campaign]
