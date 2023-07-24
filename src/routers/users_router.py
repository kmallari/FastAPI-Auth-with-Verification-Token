from fastapi import APIRouter, Depends

from db.models.user import User
from src.dependencies import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=User, response_model_exclude=["password", "disabled"])
async def get_current_user(
    user: User = Depends(get_current_active_user),
):
    return user
