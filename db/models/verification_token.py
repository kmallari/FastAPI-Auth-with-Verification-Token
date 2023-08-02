"""
Verification Token Model Module.

This module defines the SQLAlchemy model for the verification token, which is used for
account verification in the application.

Module Dependencies:
    - uuid: Library for generating unique identifiers.
    - typing.Optional: Type hint for optional values.
    - sqlalchemy.Column: Represents a column in the database table.
    - sqlalchemy.BigInteger: Represents a BigInteger column type.
    - sqlmodel.Field: Represents a field in the SQLModel.
    - sqlmodel.SQLModel: Base class for SQLModel classes.
    - datetime.datetime: Library for working with date and time.
    - random.randint: Function to generate a random integer.

Functions:
    generate_verification_token: Function to generate a random 6-digit verification token.

Class:
    VerificationToken: SQLAlchemy model representing the verification token table.

"""

import uuid
from datetime import datetime
from random import randint
from typing import Optional

from sqlalchemy import Column, BigInteger
from sqlmodel import Field, SQLModel


# generate a random 6 digit number
def generate_verification_token():
    """
    Generate a random 6-digit verification token.

    Returns:
        str: A randomly generated 6-digit verification token.

    """
    return randint(100000, 999999)


class VerificationToken(SQLModel, table=True):
    """
    Verification Token Model.

    Represents the SQLAlchemy model for the verification token table.

    Attributes:
        id (Optional[str]): The primary key for the verification token.
        token (Optional[str]): The 6-digit verification token.
        user_id (str): The user ID associated with the verification token.
        created_at (int): The timestamp when the verification token was created.
        expires_at (int): The timestamp when the verification token expires
            (5 minutes after creation).

    Note:
        The verification token is used for account verification in the application.

    """

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
