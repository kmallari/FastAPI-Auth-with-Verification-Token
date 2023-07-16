from typing import Optional

from sqlalchemy import Column, BigInteger
from sqlmodel import Field, SQLModel
import uuid
from datetime import datetime


class User(SQLModel, table=True):
    id: Optional[str] = Field(
        default=str(uuid.uuid4()),
        primary_key=True,
        max_length=36,
        min_length=36,
    )
    email: str = Field(default=None, index=True, unique=True)
    password: str = Field(default=None)
    is_verified: Optional[bool] = Field(default=False)
    disabled: Optional[bool] = Field(default=False)
    created_at: int = Field(
        default=round((datetime.now() - datetime(1970, 1, 1)).total_seconds()),
        sa_column=Column(BigInteger()),
    )
