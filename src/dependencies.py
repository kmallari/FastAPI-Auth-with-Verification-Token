"""
This module contains functions related to user authentication and access control.
It includes functions to validate request headers and tokens, decode and validate
JSON Web Tokens (JWTs), and retrieve the current authenticated and active user.

Classes:
    TokenData: A Pydantic BaseModel representing the token data extracted from a JWT.

Functions:
    get_token_header: Validate the X-Token header.
    get_query_token: Validate the query parameter token.
    get_current_user: Get the current authenticated user based on the provided token.
    get_current_active_user: Get the current active user based on the provided user from the token.

Constants:
    oauth2_scheme: An instance of OAuth2PasswordBearer representing the OAuth2 scheme.
"""

from typing import Annotated

from fastapi import Header, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel

from db.models.user import User
from src.constants import ALGORITHM, JWT_SECRET_KEY
from src.repositories.users_repo import get_user_by_email


class TokenData(BaseModel):
    email: str | None = None


async def get_token_header(x_token: Annotated[str, Header()]):
    """
    Validate the X-Token header.

    Args:
        x_token (str): The X-Token header value.

    Raises:
        HTTPException: If the X-Token header is invalid.

    Returns:
        None
    """
    if x_token != "fake-super-secret-token":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="X-Token header invalid"
        )


async def get_query_token(token: str):
    """
    Validate the query parameter token.

    Args:
        token (str): The query parameter token.

    Raises:
        HTTPException: If the token is not valid.

    Returns:
        None
    """
    if token != "jessica":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No Jessica token provided"
        )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", scheme_name="JWT")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """
    Get the current authenticated user based on the provided token.

    Args:
        token (str): The token obtained from the request.

    Raises:
        HTTPException: If the credentials cannot be validated.

    Returns:
        User: The User model representing the current user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise JWTError
        token_data = TokenData(email=email)
    except JWTError as exc:
        raise credentials_exception from exc
    user = get_user_by_email(token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get the current active user based on the provided user from the token.

    Args:
        current_user (User): The authenticated user obtained from the token.

    Raises:
        HTTPException: If the user is inactive (disabled).

    Returns:
        User: The User model representing the current active user.
    """
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user
