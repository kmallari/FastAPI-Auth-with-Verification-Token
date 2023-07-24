from datetime import datetime

from db.models.user import User
from src.repositories import verification_token_repo, users_repo
from fastapi import HTTPException, status


async def verify_user(user_id: str, token: str):
    if not token or not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token and user_id are required",
        )
    verification_token = verification_token_repo.get_latest_verification_token(user_id)

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

    verification_token_repo.verify_user(user.id)
    verification_token_repo.delete_user_verification_tokens(user.id)

    return {"ok": True}


async def retrieve_new_verification_token(user: User):
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already verified"
        )

    verification_token = verification_token_repo.get_latest_verification_token(user.id)

    if verification_token:
        if verification_token.expires_at > round(
            (datetime.now() - datetime(1970, 1, 1)).total_seconds()
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Token not expired"
            )
        verification_token_repo.delete_user_verification_tokens(user.id)

    verification_token_repo.create_verification_token(user.id)
    return {"ok": True}
