from jose import jwt, JWTError
import requests
from src.repositories import auth_repo
from src.constants import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    CLIENT_URL,
    JWT_SECRET_KEY,
    ALGORITHM,
)
import time
from urllib.parse import unquote

from src.utils.user_utils import create_access_token, create_refresh_token


async def google(code: str):
    code = unquote(code)
    print("x" * 100)
    token_url = "https://oauth2.googleapis.com/token"
    print(f"{CLIENT_URL}/auth/google/callback")
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
