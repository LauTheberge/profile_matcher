from datetime import datetime
from unittest.mock import patch, AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from profile_matcher.api.models.campaign import (
    Matcher,
    Level,
    MatcherContent,
    ActiveCampaign,
)
from profile_matcher.database.models import PlayerProfile, Clan, Inventory, Device


class TestGetClientConfig:
    @pytest.fixture(autouse=True)
    def setup_data(self, async_client, async_session):
        self.__test_clan = Clan(
            id=123456,
            name='Hello world clan',
        )

        self.__test_device = Device(
            id=1,
            player_id='97983be2-98b7-11e7-90cf-082e5f28d836',
            model='apple iphone 11',
            carrier='vodafone',
            firmware='123',
        )

    @pytest.mark.asyncio
    async def test_get_client_config(self, async_client, async_session, event_loop):
        """
        Test that the client config is returned correctly with the active campaign added.
        """

        # Arrange
        # Usually, this could be a helper factory allowing to create models and commit them to the database easily
        player_profile = PlayerProfile(
            player_id='97983be2-98b7-11e7-90cf-082e5f28d836',
            credential='apple_credential',
            created=datetime(2021, 1, 10, 13, 37, 17),
            modified=datetime(2021, 1, 23, 13, 37, 17),
            last_session=datetime(2021, 1, 23, 13, 37, 17),
            total_spent=400,
            total_refund=0,
            total_transactions=5,
            last_purchase=datetime(2021, 1, 22, 13, 37, 17),
            active_campaigns=[],
            level=3,
            xp=1000,
            total_playtime=144,
            country='CA',
            language='fr',
            birthdate=datetime(2000, 1, 10, 13, 37, 17),
            gender='male',
            clan_id=self.__test_clan.id,
            custom_field='mycustom',
        )

        test_inventory = Inventory(
            id=1,
            player_id='97983be2-98b7-11e7-90cf-082e5f28d836',
            cash=123,
            coins=123,
            item_1=1,
            item_34=3,
            item_55=2,
        )

        # Mock the campaign API response
        mock_campaign = ActiveCampaign(
            game='mygame',
            name='mocked_campaign',
            priority=10.5,
            matchers=Matcher(
                level=Level(min=1, max=3),
                has=MatcherContent(country=['US', 'RO', 'CA'], items=['item_1']),
                does_not_have=MatcherContent(items=['item_4']),
            ),
            start_date=datetime(2022, 1, 25),
            end_date=datetime(2022, 2, 25),
            enabled=True,
            last_updated=datetime(2021, 7, 13),
        )

        await self.create_data(
            async_session,
            player_profile,
            test_inventory,
            self.__test_device,
            self.__test_clan,
        )

        with patch(
            'profile_matcher.api.routes.client_config._get_client_config.__mock_campaign_api',
            new_callable=Mock,
        ) as mock_campaign_api:
            mock_campaign_api.return_value = [mock_campaign]
            # Act
            response = await async_client.get(
                f'/get_client_config/{player_profile.player_id}'
            )
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert 'mocked_campaign' in data['active_campaigns']

    @staticmethod
    async def create_data(
        async_session: AsyncSession,
        player_profile: PlayerProfile,
        inventory: Inventory,
        device: Device,
        clan: Clan,
    ):
        """
        Create data to the database.
        """
        async_session.add(clan)
        async_session.add(player_profile)
        # Sync the temporary state with the permanent state before refreshing to make data available for test_inventory
        # and test_device
        await async_session.flush()
        await async_session.refresh(player_profile)

        async_session.add(inventory)
        async_session.add(device)

        await async_session.commit()
