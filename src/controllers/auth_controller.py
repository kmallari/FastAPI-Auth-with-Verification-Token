"""
This module contains various functions related to user authentication and management.

Functions:
- google(code: str) -> dict: Authenticate users using the Google OAuth2.0 flow.
  Returns an access token and a refresh token.
- create_user(user: User) -> User: Create a new user with the provided details.
  Sends a verification email and returns the created user.
- login(email: str, password: str) -> dict: Authenticate a user with the given email
  and password. Returns an access token and a refresh token on successful login.
- verify_user(user_id: str, token: str) -> dict: Verify a user's email using the provided
  verification token. Deletes expired tokens after successful verification.
- retrieve_new_verification_token(user: User) -> dict: Request a new verification token
  for a user. Deletes any existing expired tokens.
"""

import re
from datetime import datetime
from urllib.parse import unquote

import requests
from fastapi import HTTPException, Response, status

from db.models.user import User
from src.constants import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    CLIENT_URL,
)
from src.constants import (
    PASSWORD_REGEX,
    EMAIL_REGEX,
)
from src.repositories import users_repo, auth_repo
from src.utils.auth_utils import (
    get_hashed_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    send_email,
)


async def google(token: str):
    """
    Authenticate a user using the Google OAuth2.0 authorization code.

    Parameters:
        token (str): The authorization code received from Google OAuth2.0 callback.

    Returns:
        dict: A dictionary containing access_token and refresh_token for the authenticated user.

    Raises:
        HTTPException: If there's an error during the authentication process or user creation.
    """
    try:
        token = unquote(token)
        token_url = "https://oauth2.googleapis.com/token"
        token_payload = {
            "code": token,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,  # Replace with your actual Google client secret
            "redirect_uri": f"{CLIENT_URL}/auth/google/callback",
            "grant_type": "authorization_code",
        }

        token_response = requests.post(token_url, data=token_payload, timeout=20)
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]

        # Get user info using the access token
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        userinfo_response = requests.get(
            userinfo_url, headers={"Authorization": f"Bearer {access_token}"}, timeout=5
        )
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()

        user = auth_repo.check_user_exists_with_email(user_info["email"])

        if not user:
            user = auth_repo.create_user_with_google(
                user_info["sub"],
                user_info["given_name"],
                user_info["family_name"],
                user_info["email"],
                user_info["email_verified"],
            )
        else:
            user = auth_repo.update_user_with_google(
                user_info["given_name"],
                user_info["family_name"],
                user_info["email"],
                user_info["email_verified"],
            )

        return {
            "access_token": create_access_token(user.email),
            "refresh_token": create_refresh_token(user.email),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Something went wrong", "error": str(e)},
        ) from e


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
    if not user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required"
        )
    if not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Password is required"
        )

    if not re.match(EMAIL_REGEX, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email"
        )

    if not re.match(PASSWORD_REGEX, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password must have a minimum eight characters,"
            " at least one uppercase letter, one lowercase "
            "letter and one number.",
        )
    try:
        new_user = users_repo.create_user(
            user.email, get_hashed_password(user.password)
        )
        code = auth_repo.create_verification_token(new_user.id)
        await send_email(user.email, code.token)
        return new_user

    except Exception as e:
        if "Duplicate entry" in str(e) and "\\'user.ix_user_email\\'" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already exists."
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Something went wrong", "error": str(e)},
        ) from e


async def login(response: Response, email: str, password: str):
    """
    Log in an existing user with the provided email and password.

    Parameters:
        response (Response): The response object.
        email (str): The email of the user.
        password (str): The password of the user.

    Returns:
        dict: A dictionary containing access_token and refresh_token if login is successful.

    Raises:
        HTTPException: If the user is not found or if the provided email and password are incorrect.
    """
    user = users_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    hashed_pass = user.password

    if not verify_password(password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect email or password"
        )

    access_token = create_access_token(user.email)

    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True
    )

    return {
        "access_token": access_token,
        "refresh_token": create_refresh_token(user.email),
    }


async def verify_user(user_id: str, token: str):
    """
    Verify a user's account using the verification token.

    Parameters:
        user_id (str): The ID of the user to be verified.
        token (str): The verification token for the user.

    Returns:
        dict: A dictionary containing the verification status.

    Raises:
        HTTPException: If there's an error during the verification process.
    """
    if not token or not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token and user_id are required",
        )
    verification_token = auth_repo.get_latest_verification_token(user_id)

    if not verification_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no verification token",
        )

    if verification_token.token != token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )

    if verification_token.expires_at < round(
        (datetime.now() - datetime(1970, 1, 1)).total_seconds()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired"
        )

    user = users_repo.get_user_by_id(verification_token.user_id)
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already verified"
        )

    auth_repo.verify_user(user.id)
    auth_repo.delete_user_verification_tokens(user.id)

    return {"ok": True}


async def retrieve_new_verification_token(user: User):
    """
    Retrieve a new verification token for a user who needs to be verified.

    Parameters:
        user (User): The user for whom a new verification token is needed.

    Returns:
        dict: A dictionary indicating the success of the token retrieval process.

    Raises:
        HTTPException: If the user is already verified or if there's an error in token retrieval.
    """
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already verified"
        )

    verification_token = auth_repo.get_latest_verification_token(user.id)

    if verification_token:
        if verification_token.expires_at > round(
            (datetime.now() - datetime(1970, 1, 1)).total_seconds()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Token not expired"
            )
        auth_repo.delete_user_verification_tokens(user.id)

    auth_repo.create_verification_token(user.id)
    return {"ok": True}
