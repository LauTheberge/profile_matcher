from datetime import datetime
from unittest.mock import patch, Mock, AsyncMock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

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
        # For the setup, this can either be done in every test (in order to keep them separate from each other) or
        # in the setup to reduce repetition. Here, since the player data doesn't change from one test to the other,
        # and there is a lot of data and repetition, it has been put in setup_data.
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

        self.__player_id = '97983be2-98b7-11e7-90cf-082e5f28d836'

        self.__player_profile = PlayerProfile(
            player_id=self.__player_id,
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

        self.__test_inventory = Inventory(
            id=1,
            player_id=self.__player_id,
            cash=123,
            coins=123,
            item_1=1,
            item_34=3,
            item_55=2,
        )

    @pytest.mark.asyncio
    async def test_get_client_config(self, async_client, async_session):
        """
        Test that the client config is returned correctly with all the fields, including the active campaign added.
        """
        # Arrange
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
            self.__player_profile,
            self.__test_inventory,
            self.__test_device,
            self.__test_clan,
        )

        with patch(
            'profile_matcher.api.routes.client_config._get.__mock_campaign_api',
            new_callable=Mock,
        ) as mock_campaign_api:
            mock_campaign_api.return_value = [mock_campaign]

            # Act
            response = await async_client.get(
                f'/get_client_config/{self.__player_profile.player_id}'
            )

        # Get the player from the database to confirm that it has been updated
        statement = select(PlayerProfile).where(
            PlayerProfile.player_id == self.__player_id
        )
        result = await async_session.exec(statement)
        player_from_database = result.first()

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data['active_campaigns'] == ['mocked_campaign']
        # Assert that the data is correctly updated in the database
        assert player_from_database.active_campaigns == ['mocked_campaign']

    @pytest.mark.asyncio
    async def test_no_campaign(self, async_client, async_session):
        """
        Test that the client config is returned correctly with no active campaign if there is none active
        """
        # Arrange
        await self.create_data(
            async_session,
            self.__player_profile,
            self.__test_inventory,
            self.__test_device,
            self.__test_clan,
        )

        with patch(
            'profile_matcher.api.routes.client_config._get.__mock_campaign_api',
            new_callable=Mock,
        ) as mock_campaign_api:
            mock_campaign_api.return_value = []
            # Act
            response = await async_client.get(
                f'/get_client_config/{self.__player_profile.player_id}'
            )
        # Get the data from the table to see that it has not been updated
        statement = select(PlayerProfile).where(
            PlayerProfile.player_id == self.__player_id
        )
        result = await async_session.exec(statement)
        player_from_database = result.first()

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data['active_campaigns'] == []
        assert player_from_database.active_campaigns == []

    @pytest.mark.asyncio
    async def test_campaign_no_match(self, async_client, async_session):
        """
        Test that the client config is returned correctly with no active campaign if there is none that matches,
        even if it's active
        """
        # Mock the campaign API response
        mock_campaign_wrong_level = ActiveCampaign(
            game='mygame',
            name='mocked_campaign',
            priority=10.5,
            matchers=Matcher(
                level=Level(min=1, max=2),
                has=MatcherContent(country=['US', 'RO', 'CA'], items=['item_1']),
                does_not_have=MatcherContent(items=['item_4']),
            ),
            start_date=datetime(2022, 1, 25),
            end_date=datetime(2022, 2, 25),
            enabled=True,
            last_updated=datetime(2021, 7, 13),
        )

        mock_campaign_wrong_country = ActiveCampaign(
            game='mygame',
            name='mocked_campaign',
            priority=10.5,
            matchers=Matcher(
                level=Level(min=1, max=3),
                has=MatcherContent(country=['US', 'RO'], items=['item_1']),
                does_not_have=MatcherContent(items=['item_4']),
            ),
            start_date=datetime(2022, 1, 25),
            end_date=datetime(2022, 2, 25),
            enabled=True,
            last_updated=datetime(2021, 7, 13),
        )

        mock_campaign_wrong_has_item = ActiveCampaign(
            game='mygame',
            name='mocked_campaign',
            priority=10.5,
            matchers=Matcher(
                level=Level(min=1, max=3),
                has=MatcherContent(country=['US', 'RO', 'CA'], items=['item_4']),
                does_not_have=MatcherContent(items=[]),
            ),
            start_date=datetime(2022, 1, 25),
            end_date=datetime(2022, 2, 25),
            enabled=True,
            last_updated=datetime(2021, 7, 13),
        )

        mock_campaign_wrong_not_has_item = ActiveCampaign(
            game='mygame',
            name='mocked_campaign',
            priority=10.5,
            matchers=Matcher(
                level=Level(min=1, max=3),
                has=MatcherContent(country=['US', 'RO', 'CA'], items=['item_1']),
                does_not_have=MatcherContent(items=['item_34']),
            ),
            start_date=datetime(2022, 1, 25),
            end_date=datetime(2022, 2, 25),
            enabled=True,
            last_updated=datetime(2021, 7, 13),
        )

        await self.create_data(
            async_session,
            self.__player_profile,
            self.__test_inventory,
            self.__test_device,
            self.__test_clan,
        )

        with patch(
            'profile_matcher.api.routes.client_config._get.__mock_campaign_api',
            new_callable=Mock,
        ) as mock_campaign_api:
            mock_campaign_api.return_value = [
                mock_campaign_wrong_level,
                mock_campaign_wrong_country,
                mock_campaign_wrong_has_item,
                mock_campaign_wrong_not_has_item,
            ]
            # Act
            response = await async_client.get(
                f'/get_client_config/{self.__player_profile.player_id}'
            )

            # Get the data from the table to see that it has not been updated
            statement = select(PlayerProfile).where(
                PlayerProfile.player_id == self.__player_id
            )
            result = await async_session.exec(statement)
            player_from_database = result.first()

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data['active_campaigns'] == []
        assert player_from_database.active_campaigns == []

    @pytest.mark.asyncio
    async def test_campaign_present_valid(self, async_client, async_session):
        """
        Test that if the campaign is already present and is still active and valid, it is not added again.
        """
        self.__player_profile.active_campaigns = ['mocked_campaign']
        # Arrange
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
            self.__player_profile,
            self.__test_inventory,
            self.__test_device,
            self.__test_clan,
        )

        with patch(
            'profile_matcher.api.routes.client_config._get.__mock_campaign_api',
            new_callable=Mock,
        ) as mock_campaign_api:
            mock_campaign_api.return_value = [mock_campaign]
            # Get the player from the database to confirm that the campaign was present before
            statement = select(PlayerProfile).where(
                PlayerProfile.player_id == self.__player_id
            )
            result = await async_session.exec(statement)
            initial_database_player = result.first()
            assert initial_database_player.active_campaigns == ['mocked_campaign']

            # Act
            response = await async_client.get(
                f'/get_client_config/{self.__player_profile.player_id}'
            )

        # Get the player from the database to confirm that it has been updated
        statement = select(PlayerProfile).where(
            PlayerProfile.player_id == self.__player_id
        )
        result = await async_session.exec(statement)
        player_from_database = result.first()

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data['active_campaigns'] == ['mocked_campaign']
        # Assert that the data is correctly updated in the database
        assert player_from_database.active_campaigns == ['mocked_campaign']

    @pytest.mark.asyncio
    async def test_campaign_present_not_valid(self, async_client, async_session):
        """
        Test that if the campaign is present in the user profile and is active, but is no longer valid for the
        player, it is removed. All other valid campaigns are kept.
        """
        self.__player_profile.active_campaigns = [
            'mocked_invalid_campaign',
            'mocked_valid_campaign',
        ]
        # Arrange
        # Mock the campaign API response
        mock_invalid_campaign = ActiveCampaign(
            game='mygame',
            name='mocked_invalid_campaign',
            priority=10.5,
            matchers=Matcher(
                level=Level(min=1, max=2),
                has=MatcherContent(country=['US', 'RO', 'CA'], items=['item_1']),
                does_not_have=MatcherContent(items=['item_4']),
            ),
            start_date=datetime(2022, 1, 25),
            end_date=datetime(2022, 2, 25),
            enabled=True,
            last_updated=datetime(2021, 7, 13),
        )

        mock_valid_campaign = ActiveCampaign(
            game='mygame',
            name='mocked_valid_campaign',
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
            self.__player_profile,
            self.__test_inventory,
            self.__test_device,
            self.__test_clan,
        )

        with patch(
            'profile_matcher.api.routes.client_config._get.__mock_campaign_api',
            new_callable=Mock,
        ) as mock_campaign_api:
            mock_campaign_api.return_value = [
                mock_invalid_campaign,
                mock_valid_campaign,
            ]
            # Get the player from the database to confirm that the campaign was present before
            statement = select(PlayerProfile).where(
                PlayerProfile.player_id == self.__player_id
            )
            result = await async_session.exec(statement)
            initial_database_player = result.first()
            assert initial_database_player.active_campaigns == [
                'mocked_invalid_campaign',
                'mocked_valid_campaign',
            ]

            # Act
            response = await async_client.get(
                f'/get_client_config/{self.__player_profile.player_id}'
            )

        # Get the player from the database to confirm that it has been updated
        statement = select(PlayerProfile).where(
            PlayerProfile.player_id == self.__player_id
        )
        result = await async_session.exec(statement)
        player_from_database = result.first()

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data['active_campaigns'] == ['mocked_valid_campaign']
        # Assert that the data is correctly updated in the database
        assert player_from_database.active_campaigns == ['mocked_valid_campaign']

    @pytest.mark.asyncio
    async def test_campaign_present_not_longer_active(
        self, async_client, async_session
    ):
        """
        Test that if the campaign was present and valid, but is no longer active (not returned by API), it is removed.
        """
        self.__player_profile.active_campaigns = ['mocked_campaign']
        # Arrange
        await self.create_data(
            async_session,
            self.__player_profile,
            self.__test_inventory,
            self.__test_device,
            self.__test_clan,
        )

        with patch(
            'profile_matcher.api.routes.client_config._get.__mock_campaign_api',
            new_callable=Mock,
        ) as mock_campaign_api:
            mock_campaign_api.return_value = []
            # Get the player from the database to confirm that the campaign was present before
            statement = select(PlayerProfile).where(
                PlayerProfile.player_id == self.__player_id
            )
            result = await async_session.exec(statement)
            initial_database_player = result.first()
            assert initial_database_player.active_campaigns == ['mocked_campaign']

            # Act
            response = await async_client.get(
                f'/get_client_config/{self.__player_profile.player_id}'
            )

        # Get the player from the database to confirm that it has been updated
        statement = select(PlayerProfile).where(
            PlayerProfile.player_id == self.__player_id
        )
        result = await async_session.exec(statement)
        player_from_database = result.first()

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data['active_campaigns'] == []
        # Assert that the data is correctly updated in the database
        assert player_from_database.active_campaigns == []

    @pytest.mark.asyncio
    async def test_player_not_found(self, async_client, async_session):
        """
        Test that 404 is returned if the player is not found.
        """
        # Arrange
        wrong_player_id = '66983be2-98b7-11e7-90cf-082e5f28d866'
        await self.create_data(
            async_session,
            self.__player_profile,
            self.__test_inventory,
            self.__test_device,
            self.__test_clan,
        )

        response = await async_client.get(f'/get_client_config/{wrong_player_id}')
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_campaign_raise(self, async_client, async_session):
        """
        Test that an Internal server error is returned if the campaign API raises an exception.
        """
        # Arrange
        await self.create_data(
            async_session,
            self.__player_profile,
            self.__test_inventory,
            self.__test_device,
            self.__test_clan,
        )

        with patch(
            'profile_matcher.api.routes.client_config._get.__mock_campaign_api',
            side_effect=Exception,
        ):
            # Act
            response = await async_client.get(
                f'/get_client_config/{self.__player_profile.player_id}'
            )

        # Assert
        assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_database_error(self, async_client, async_session):
        """
        Test that an Internal server error is returned if the database raises an exception.
        """
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
            self.__player_profile,
            self.__test_inventory,
            self.__test_device,
            self.__test_clan,
        )
        # We patch the second commit of the route to return a database error.
        with patch.object(
            async_session,
            'commit',
            new=AsyncMock(side_effect=[None, SQLAlchemyError('Database error')]),
        ):
            with patch(
                'profile_matcher.api.routes.client_config._get.__mock_campaign_api',
                new_callable=Mock,
            ) as mock_campaign_api:
                mock_campaign_api.return_value = [mock_campaign]

                # Act
                response = await async_client.get(
                    f'/get_client_config/{self.__player_profile.player_id}'
                )

        assert response.status_code == 500

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
