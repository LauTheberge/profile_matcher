from datetime import datetime
from logging import Logger

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from profile_matcher.api.models.campaign import (
    ActiveCampaign,
    Matcher,
    Level,
    MatcherContent,
)
from profile_matcher.api.models.error_response import ErrorResponse
from profile_matcher.api.models.player_profile_response import PlayerProfileResponse
from profile_matcher.database import get_db_session
from profile_matcher.database.models import PlayerProfile, Inventory

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

logger = Logger('Get_client_config')


@router.get(
    '/get_client_config/{player_id}',
    response_model=PlayerProfileResponse,
    response_model_exclude_none=True,
    responses={
        404: {'model': ErrorResponse, 'description': 'Player not found'},
        500: {'model': ErrorResponse, 'description': 'Internal server error'},
    },
)
async def get_client_config(
    player_id: str, session: AsyncSession = Depends(get_db_session)
):
    """
    Return the player profile with the active campaign added
    """
    statement = select(PlayerProfile).where(PlayerProfile.player_id == player_id)
    result = await session.exec(statement)
    player = result.first()
    if player is None:
        logger.debug(f'No player found with id {player_id}')
        raise HTTPException(
            status_code=404, detail=f'No player found with id {player_id}'
        )

    # Commit to avoid idle in transaction before (mocked) external call
    await session.commit()

    active_campaigns: list[ActiveCampaign] = mock_campaign_api()

    # Refresh the database to recuperate the player
    await session.refresh(player)

    player.active_campaigns = remove_inactive_campaigns(
        player.active_campaigns, active_campaigns
    )

    for active_campaign in active_campaigns:
        # If the match is already present in the list and still a match, it stays there, if it was present and is no
        # longer a match, it is removed. If it's valid and was not previously in the list, it is added.
        is_a_match = validate_player_and_campaign_match(player, active_campaign)
        campaign_name = active_campaign.name

        if is_a_match and campaign_name not in player.active_campaigns:
            player.active_campaigns.append(campaign_name)
        elif not is_a_match and campaign_name in player.active_campaigns:
            player.active_campaigns.remove(campaign_name)

    # Update the database with the new player info
    try:
        session.add(player)
        await session.commit()
        await session.refresh(player)
    except Exception as e:
        logger.error(f'Error in committing active campaign to database: {e}')
        raise HTTPException(
            status_code=500,
            detail='Something went wrong while getting the client config.',
        )

    return player


def remove_inactive_campaigns(
    player_campaign_list: list[str], active_campaigns: list[ActiveCampaign]
) -> list[str]:
    """
    This does a first pass to remove the campaigns that are not active anymore. This happens if the player has a
    campaign in the database that is not returned by the external service.
    """
    logger.debug(f'Removing inactive campaigns from {player_campaign_list}')
    active_campaign_names = {campaign.name for campaign in active_campaigns}

    return [
        campaign
        for campaign in player_campaign_list
        if campaign in active_campaign_names
    ]


def validate_player_and_campaign_match(
    player: PlayerProfileResponse, campaign: ActiveCampaign
) -> bool:
    """
    Match the player and campaign. The level of the player must be within the level range of the campaign, must have the
    right country, the items required by the campaign, and must not have the items that are not allowed by the
    campaign.
    """
    logger.debug(f'Validating player {player} with campaign {campaign}')
    player_items = parse_items(player.inventory)

    return (
        (
            (campaign.matchers.level.min <= player.level <= campaign.matchers.level.max)
            and (set(player_items).intersection(campaign.matchers.has.items))
        )
        and (player.country in campaign.matchers.has.country)
    ) and (not set(player_items).intersection(campaign.matchers.does_not_have.items))


def parse_items(inventory: Inventory) -> list[str]:
    """
    Parse the items from the inventory that are not None into a list of strings. Only the name (first element of the
    tuple) is needed.
    """
    logger.debug(f'Parsing items from inventory: {inventory}')
    return [key for key, value in inventory.model_dump().items() if value is not None]


def mock_campaign_api() -> list[ActiveCampaign]:
    """
    This mock an external api call to get all the active campaigns
    """
    campaign_level = Level(min=1, max=3)
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
