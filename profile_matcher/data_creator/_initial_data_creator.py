from datetime import datetime
from logging import Logger

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from profile_matcher.database.models import Device, Inventory, PlayerProfile, Clan

# This is for the test purpose (in order to seed the database with the test data)
# In a normal scenario, this data would be coming from the client application.


class InitialDataCreator:
    def __init__(self):
        self.logger = Logger(__name__)

    async def create_data(self, session: AsyncSession):
        """
        Create data for testing purposes. In a real-world scenario, this data would come from the client.
        """
        self.logger.info('Creating initial data')
        test_clan = Clan(
            id=123456,
            name='Hello world clan',
        )

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
            clan_id=test_clan.id,
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

        test_device = Device(
            id=1,
            player_id='97983be2-98b7-11e7-90cf-082e5f28d836',
            model='apple iphone 11',
            carrier='vodafone',
            firmware='123',
        )
        session.add(test_clan)
        session.add(player_profile)
        # Sync the temporary state with the permanent state before refreshing to make data available for test_inventory
        # and test_device
        await session.flush()
        await session.refresh(player_profile)

        session.add(test_inventory)
        session.add(test_device)

        await session.commit()

    async def try_create_data(self, session: AsyncSession):
        """
        Try to create the data. If the data already exists, do nothing
        Once again, in a real-world scenario, this would not be present, as the data would be coming from the client.
        This is to prevent the program from trying to create the same data multiple times.
        """
        self.logger.info('Trying to create data')
        statement_player = select(PlayerProfile)
        statement_clan = select(Clan)
        result_player = await session.exec(statement_player)
        result_clan = await session.exec(statement_clan)
        if not result_player.first() and not result_clan.first():
            self.logger.debug('Data does not exist. Creating data')
            await self.create_data(session)
