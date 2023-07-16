import re

from db.models.user import User
from src.repositories import users_repo, verification_token_repo
from fastapi import HTTPException, status
from src.constants import (
    PASSWORD_REGEX,
    EMAIL_REGEX,
)
from src.utils.user_utils import (
    get_hashed_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)


def create_user(user: User):
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
        verification_token_repo.create_verification_token(new_user.id)
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


def login(email: str, password: str):
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
