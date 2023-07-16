from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from db.models.user import User
from src.controllers import users_controller
from src.dependencies import get_current_active_user

router = APIRouter()


@router.post("/")
async def create_user(user: User):
    return users_controller.create_user(user)


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return users_controller.login(form_data.username, form_data.password)


@router.get("/me")
async def get_current_user(user: User = Depends(get_current_active_user)):
    return user


@router.post("/verify/new")
async def send_verification_email(user: User = Depends(get_current_active_user)):
    return users_controller.retrieve_new_verification_token(user)


@router.post("/verify/{token}")
async def verify_user(token: str, user: User = Depends(get_current_active_user)):
    return users_controller.verify_user(user.id, token)
