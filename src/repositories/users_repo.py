"""
This module contains functions related to user management and retrieval.

Functions:
    create_user(email: str, password: str) -> User:
        Create a new user with the provided email and password.

    get_user_by_email(email: str) -> User | None:
        Retrieve a user by their email.

    get_user_by_id(user_id: str) -> User | None:
        Retrieve a user by their unique ID.

Note:
    This module depends on the following:
        - db.models.user.User: The User model for user data.
        - db.engine.engine: The SQLAlchemy engine for database connection.

Please ensure that these dependencies are satisfied before using the functions in this module for
user creation and retrieval.
"""

from sqlmodel import Session, select

from db.engine import engine
from db.models.user import User


def create_user(email: str, password: str):
    """
    Create a new user with the provided email and password.

    Parameters:
        email (str): The email of the new user.
        password (str): The password of the new user.

    Returns:
        User: The newly created User object.

    Raises:
        <Any specific exceptions that might occur during user creation>
    """
    user = User(email=email, password=password)
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def get_user_by_email(email: str):
    """
    Retrieve a user by their email.

    Parameters:
        email (str): The email of the user to retrieve.

    Returns:
        User | None: If a user with the specified email exists, returns the User object;
                     otherwise, returns None.

    Raises:
        <Any specific exceptions that might occur during user retrieval>
    """
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        return user


def get_user_by_id(user_id: str):
    """
    Retrieve a user by their unique ID.

    Parameters:
        user_id (str): The unique ID of the user to retrieve.

    Returns:
        User | None: If a user with the specified ID exists, returns the User object;
                     otherwise, returns None.

    Raises:
        <Any specific exceptions that might occur during user retrieval>
    """
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()
        return user
