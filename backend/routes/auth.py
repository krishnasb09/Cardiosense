from fastapi import APIRouter, Depends

from backend.models.schemas import AuthUser
from backend.utils.security import get_current_user

router = APIRouter()


@router.get("/me", response_model=AuthUser)
async def me(user: AuthUser = Depends(get_current_user)):
    return user
