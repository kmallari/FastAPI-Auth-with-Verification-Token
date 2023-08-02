"""
User Model Module.

This module defines the User model class, which represents a user in the database.
The User model contains various attributes representing user information, such as
the unique identifier, authentication details, personal information, and timestamps.

Module Dependencies:
    - uuid: A module to generate unique identifiers (UUIDs).
    - datetime: A module to work with date and time information.
    - typing: A module for type hints.
    - sqlmodel: A library for defining and working with SQL database models.

Classes:
    User: Represents a user in the database.

Attributes:
    (See the class docstring for a detailed description of the attributes.)

"""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Column, BigInteger


class User(SQLModel, table=True):
    """
    User Model.

    Represents a user in the database.

    Attributes:
        id (str): The unique identifier of the user.
        sub (Optional[str]): The subject identifier used for external authentication (e.g., Google).
        email (str): The email address of the user.
        password (str): The hashed password of the user.
        provider (str): The authentication provider (e.g., "local" or "google").
        given_name (Optional[str]): The given name (first name) of the user.
        family_name (Optional[str]): The family name (last name) of the user.
        is_verified (Optional[bool]): A flag indicating whether the user is verified.
        disabled (Optional[bool]): A flag indicating whether the user is disabled.
        created_at (int): The Unix timestamp (seconds since 1970) when the user was created.
    """

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
