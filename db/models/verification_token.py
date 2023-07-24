import uuid
from typing import Optional

from sqlalchemy import Column, BigInteger
from sqlmodel import Field, SQLModel
from datetime import datetime
from random import randint


# generate a random 6 digit number
def generate_verification_token():
    return randint(100000, 999999)


class VerificationToken(SQLModel, table=True):
    id: Optional[str] = Field(
        primary_key=True,
        max_length=36,
        min_length=36,
        default_factory=lambda: str(uuid.uuid4()),
    )
    token: Optional[str] = Field(
        default_factory=generate_verification_token,
        max_length=6,
        min_length=6,
    )
    user_id: str = Field(
        index=True,
        max_length=36,
        min_length=36,
    )
    created_at: int = Field(
        sa_column=Column(BigInteger()),
        default_factory=lambda: round(
            (datetime.now() - datetime(1970, 1, 1)).total_seconds()
        ),
    )
    expires_at: int = Field(
        # expires in 5 minutes
        default_factory=lambda: round(
            (datetime.now() - datetime(1970, 1, 1)).total_seconds() + 300
        ),
        sa_column=Column(BigInteger()),
    )
