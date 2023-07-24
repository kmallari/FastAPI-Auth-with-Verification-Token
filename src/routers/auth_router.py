from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from src.controllers import auth_controller
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import JSONTokens, Ok
from db.models.user import User
from src.dependencies import get_current_active_user

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login", scheme_name="JWT")


@router.post("/google")
async def google_login(request: Request, code: str):
    # Exchange the authorization code with an access token
    print("code: ", code)
    return await auth_controller.google(code)


@router.post(
    "/register", response_model=User, response_model_exclude=["password", "disabled"]
)
async def create_user(user: User):
    return await auth_controller.create_user(user)


@router.post("/login", response_model=JSONTokens)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await auth_controller.login(form_data.username, form_data.password)


@router.post("/verify/new", response_model=Ok)
async def send_verification_email(user: User = Depends(get_current_active_user)):
    return await auth_controller.retrieve_new_verification_token(user)


@router.post("/verify/{token}", response_model=Ok)
async def verify_user(token: str, user: User = Depends(get_current_active_user)):
    return await auth_controller.verify_user(user.id, token)
