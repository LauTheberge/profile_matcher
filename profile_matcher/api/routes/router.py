from fastapi import APIRouter, FastAPI, Depends

from profile_matcher.api.dependencies.session import get_db_session

app = FastAPI()
router = APIRouter(dependencies=[Depends(get_db_session)])

