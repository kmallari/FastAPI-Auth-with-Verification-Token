from typing import Optional

from sqlmodel import Field, SQLModel, Column, BigInteger
import uuid
from datetime import datetime


class User(SQLModel, table=True):
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid.uuid4()),
    )
    sub: Optional[str] = Field(default=None, index=True, unique=True)
    email: str = Field(default=None, index=True, unique=True)
    password: str = Field(default=None)
    provider: str = Field(default="local")
    given_name: Optional[str] = Field(default=None)
    family_name: Optional[str] = Field(default=None)
    is_verified: Optional[bool] = Field(default=False)
    disabled: Optional[bool] = Field(default=False)
    created_at: int = Field(
        default_factory=lambda: round(
            (datetime.now() - datetime(1970, 1, 1)).total_seconds()
        ),
        sa_column=Column(BigInteger()),
    )
