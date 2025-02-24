import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from profile_matcher.database import get_db_session
from profile_matcher.database.models import PlayerProfile, Inventory
from ...models import (
    ActiveCampaign,
    Matcher,
    Level,
    MatcherContent,
    ErrorResponse,
    PlayerProfileResponse,
)

router = APIRouter()

logger = logging.getLogger('uvicorn')


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

    try:
        active_campaigns: list[ActiveCampaign] = __mock_campaign_api()
    # Here, we would except the specific exception that can be raised from the service. Since we do not raise a specific
    # exception, we use "Exception"
    except Exception as e:
        logger.error(f'Error in getting active campaigns: {e}')
        raise HTTPException(
            status_code=500,
            detail='Something went wrong while getting the client config.',
        )

    # Refresh the database to recuperate the player
    await session.refresh(player)

    player.active_campaigns = __remove_inactive_campaigns(
        player.active_campaigns, active_campaigns
    )

    for active_campaign in active_campaigns:
        # If the match is already present in the list and still a match, it stays there, if it was present and is no
        # longer a match, it is removed. If it's valid and was not previously in the list, it is added.
        is_a_match = __validate_player_and_campaign_match(player, active_campaign)
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
    except SQLAlchemyError as e:
        logger.error(f'Error in committing active campaign to database: {e}')
        raise HTTPException(
            status_code=500,
            detail='Something went wrong while getting the client config.',
        )

    return player


def __remove_inactive_campaigns(
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


def __validate_player_and_campaign_match(
    player: PlayerProfileResponse, campaign: ActiveCampaign
) -> bool:
    """
    Match the player and campaign. The level of the player must be within the level range of the campaign, must have the
    right country, the items required by the campaign, and must not have the items that are not allowed by the
    campaign.
    """
    logger.debug(f'Validating player {player} with campaign {campaign}')
    player_items = __parse_items(player.inventory)

    return (
        (
            (campaign.matchers.level.min <= player.level <= campaign.matchers.level.max)
            and (set(player_items).intersection(campaign.matchers.has.items))
        )
        and (player.country in campaign.matchers.has.country)
    ) and (not set(player_items).intersection(campaign.matchers.does_not_have.items))


def __parse_items(inventory: Inventory) -> list[str]:
    """
    Parse the items from the inventory that are not None into a list of strings. Only the name (first element of the
    tuple) is needed.
    """
    logger.debug(f'Parsing items from inventory: {inventory}')
    return [key for key, value in inventory.model_dump().items() if value is not None]


def __mock_campaign_api() -> list[ActiveCampaign]:
    """
    This mock the external api call to get all the active campaigns
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
