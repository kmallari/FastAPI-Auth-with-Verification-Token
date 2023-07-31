"""
This APIRouter provides endpoints related to user authentication and verification.

Endpoints:
    POST /google:
        Authenticate a user using the Google OAuth2.0 authorization code.

    POST /register:
        Create a new user with the provided user details.

    POST /login:
        Log in an existing user with the provided email and password.

    POST /verify/new:
        Retrieve a new verification token for a user who needs to be verified.

    POST /verify/{token}:
        Verify a user's account using the verification token.

Note:
    This APIRouter uses various dependencies and controllers to handle user authentication
    and verification.
    Ensure that all necessary dependencies are properly configured before using these endpoints.

Dependencies:
    - get_current_active_user: A dependency function to get the currently active user
      for verification.

Controllers:
    - auth_controller.google(code: str) -> dict:
        Authentication controller function for Google OAuth2.0 authorization.

    - auth_controller.create_user(user: User) -> User:
        Controller function to create a new user with the provided details.

    - auth_controller.login(email: str, password: str) -> dict:
        Controller function to log in an existing user with the provided email and password.

    - auth_controller.retrieve_new_verification_token(user: User) -> dict:
        Controller function to retrieve a new verification token for a user who needs to be
        verified.

    - auth_controller.verify_user(user_id: str, token: str) -> dict:
        Controller function to verify a user's account using the verification token.
"""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.requests import Request

from db.models.user import User
from src.controllers import auth_controller
from src.dependencies import get_current_active_user
from src.schemas import JSONTokens, Ok

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", scheme_name="JWT")


@router.post("/google")
async def google_login(request: Request, code: str):
    """
    Authenticate a user using the Google OAuth2.0 authorization code.

    Parameters:
        request (Request): The HTTP request object.
        code (str): The authorization code received from Google OAuth2.0 callback.

    Returns:
        dict: A dictionary containing access_token and refresh_token for the authenticated user.

    Raises:
        HTTPException: If there's an error during the authentication process or user creation.
    """
    return await auth_controller.google(code)


@router.post(
    "/register", response_model=User, response_model_exclude=["password", "disabled"]
)
async def create_user(user: User):
    """
    Create a new user with the provided user details.

    Parameters:
        user (User): An instance of the User model containing user details.

    Returns:
        User: The newly created user.

    Raises:
        HTTPException: If there's an error during user creation or validation fails.
    """
    return await auth_controller.create_user(user)


@router.post("/login", response_model=JSONTokens)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Log in an existing user with the provided email and password.

    Parameters:
        form_data (OAuth2PasswordRequestForm, optional): The OAuth2 password request form data.

    Returns:
        dict: A dictionary containing access_token and refresh_token if login is successful.

    Raises:
        HTTPException: If the user is not found or if the provided email and password are incorrect.
    """
    return await auth_controller.login(form_data.username, form_data.password)


@router.post("/verify/new", response_model=Ok)
async def send_verification_email(user: User = Depends(get_current_active_user)):
    """
    Retrieve a new verification token for a user who needs to be verified.

    Parameters:
        user (User, optional): The user for whom a new verification token is needed.

    Returns:
        dict: A dictionary indicating the success of the token retrieval process.

    Raises:
        HTTPException: If the user is already verified or if there's an error during
        token retrieval.
    """
    return await auth_controller.retrieve_new_verification_token(user)


@router.post("/verify/{token}", response_model=Ok)
async def verify_user(token: str, user: User = Depends(get_current_active_user)):
    """
    Verify a user's account using the verification token.

    Parameters:
        token (str): The verification token for the user.
        user (User, optional): The user to be verified.

    Returns:
        dict: A dictionary containing the verification status.

    Raises:
        HTTPException: If there's an error during the verification process.
    """
    return await auth_controller.verify_user(user.id, token)
