
from .router import router
from profile_matcher.core.database.models import PlayerProfile


@router.get("/get_client_config/{player_id}", response_model=PlayerProfile)
async def get_client_config(player_id: int):
    pass
