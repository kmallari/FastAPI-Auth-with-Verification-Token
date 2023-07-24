from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from src.controllers import auth_controller


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login", scheme_name="JWT")


# login using google
@router.get("/google")
async def google_login(request: Request, code: str):
    # Exchange the authorization code with an access token
    print("code: ", code)
    return await auth_controller.google(code)
