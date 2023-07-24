import requests
from src.repositories import auth_repo
from src.constants import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    CLIENT_URL,
)
import time
from urllib.parse import unquote

import re

from db.models.user import User
from src.repositories import users_repo, auth_repo
from fastapi import HTTPException, status
from src.constants import (
    PASSWORD_REGEX,
    EMAIL_REGEX,
)
from src.utils.auth_utils import (
    get_hashed_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)

from datetime import datetime


async def google(code: str):
    code = unquote(code)
    token_url = "https://oauth2.googleapis.com/token"
    token_payload = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,  # Replace with your actual Google client secret
        "redirect_uri": f"{CLIENT_URL}/auth/google/callback",
        "grant_type": "authorization_code",
    }

    start = time.time()
    token_response = requests.post(token_url, data=token_payload)
    token_response.raise_for_status()
    access_token = token_response.json()["access_token"]
    end = time.time()
    print(f"Time taken: {end - start}")

    start = time.time()
    # Get user info using the access token
    userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    userinfo_response = requests.get(
        userinfo_url, headers={"Authorization": f"Bearer {access_token}"}
    )
    userinfo_response.raise_for_status()
    user_info = userinfo_response.json()
    end = time.time()
    print(f"Time taken: {end - start}")

    print(user_info)
    # Process user_info as needed

    # Check if user is in the database
    # If not, create a new user
    # If yes, update the user's information
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

    # Generate a JWT token with user information
    print("user", user)

    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email),
    }


async def create_user(user: User):
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
            detail="Password must have a minimum eight characters, at least one uppercase letter, one lowercase "
            "letter and one number.",
        )
    try:
        new_user = users_repo.create_user(
            user.email, get_hashed_password(user.password)
        )
        auth_repo.create_verification_token(new_user.id)
        return new_user

    except Exception as e:
        if "Duplicate entry" in str(e) and "\\'user.ix_user_email\\'" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already exists."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Something went wrong", "error": str(e)},
        )


async def login(email: str, password: str):
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

    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email),
    }


async def verify_user(user_id: str, token: str):
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
