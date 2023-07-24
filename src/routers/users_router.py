from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from db.models.user import User
from src.controllers import users_controller, verification_token_controller
from src.dependencies import get_current_active_user
from src.schemas import JSONTokens, Ok

router = APIRouter()


@router.post("/", response_model=User, response_model_exclude=["password", "disabled"])
async def create_user(user: User):
    return await users_controller.create_user(user)


@router.post("/login", response_model=JSONTokens)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await users_controller.login(form_data.username, form_data.password)


@router.get("/me", response_model=User, response_model_exclude=["password", "disabled"])
async def get_current_user(
    user: User = Depends(get_current_active_user),
):
    return user


@router.post("/verify/new", response_model=Ok)
async def send_verification_email(user: User = Depends(get_current_active_user)):
    return await verification_token_controller.retrieve_new_verification_token(user)


@router.post("/verify/{token}", response_model=Ok)
async def verify_user(token: str, user: User = Depends(get_current_active_user)):
    return await verification_token_controller.verify_user(user.id, token)
