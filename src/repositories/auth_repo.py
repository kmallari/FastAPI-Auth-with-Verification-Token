"""
This module contains functions related to user authentication and verification.

Functions:
    check_user_exists_with_email(email: str) -> User | None:
        Check if a user with the given email exists.

    create_user_with_google(sub: str, given_name: str, family_name: str,
                            email: str, email_verified: bool) -> User:
        Create a new user with the provided Google OAuth2.0 user details.

    update_user_with_google(given_name: str, family_name: str, email: str,
                            email_verified: bool) -> User:
        Update an existing user's details with the provided Google OAuth2.0 user details.

    create_verification_token(user_id: str) -> VerificationToken:
        Create a new verification token for the user.

    get_latest_verification_token(user_id: str) -> VerificationToken | None:
        Retrieve the latest verification token for the user.

    verify_user(user_id: str) -> User:
        Mark the user with the given ID as verified.

    delete_user_verification_tokens(user_id: str) -> None:
        Delete all verification tokens associated with the user.

Note:
    This module depends on the following:
        - db.models.verification_token.VerificationToken: The VerificationToken model for
          user verification.
        - db.models.user.User: The User model for user data.
        - db.engine.engine: The SQLAlchemy engine for database connection.

Please ensure that these dependencies are satisfied before using the functions in this module for
user authentication and verification processes.
"""

from sqlmodel import Session, select
from db.models.verification_token import VerificationToken

from db.models.user import User
from db.engine import engine


def check_user_exists_with_email(email: str):
    """
    Check if a user with the given email exists.

    Parameters:
        email (str): The email to check for.

    Returns:
        User | None: If the user with the specified email exists, returns the User object;
                     otherwise, returns None.
    """
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        return user


def create_user_with_google(
    sub: str, given_name: str, family_name: str, email: str, email_verified: bool
):
    """
    Create a new user with the provided Google OAuth2.0 user details.

    Parameters:
        sub (str): The Google user's unique identifier.
        given_name (str): The given name (first name) of the user.
        family_name (str): The family name (last name) of the user.
        email (str): The email of the user.
        email_verified (bool): Indicates if the user's email has been verified.

    Returns:
        User: The newly created User object.

    Raises:
        <Any specific exceptions that might occur during the creation process>
    """
    user = User(
        sub=sub,
        given_name=given_name,
        family_name=family_name,
        email=email,
        is_verified=email_verified,
        provider="google",
    )
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def update_user_with_google(
    given_name: str, family_name: str, email: str, email_verified: bool
):
    """
    Update an existing user's details with the provided Google OAuth2.0 user details.

    Parameters:
        given_name (str): The updated given name (first name) of the user.
        family_name (str): The updated family name (last name) of the user.
        email (str): The email of the user.
        email_verified (bool): Indicates if the user's email has been verified.

    Returns:
        User: The updated User object.

    Raises:
        <Any specific exceptions that might occur during the update process>
    """
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        user.given_name = given_name
        user.family_name = family_name
        user.is_verified = email_verified
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def create_verification_token(user_id: str):
    """
    Create a new verification token for the user.

    Parameters:
        user_id (str): The ID of the user for whom the token is created.

    Returns:
        VerificationToken: The newly created VerificationToken object.

    Raises:
        <Any specific exceptions that might occur during the token creation process>
    """

    with Session(engine) as session:
        verification_token = VerificationToken(user_id=user_id)
        session.add(verification_token)
        session.commit()
        session.refresh(verification_token)
        return verification_token


def get_latest_verification_token(user_id: str):
    """
    Retrieve the latest verification token for the user.

    Parameters:
        user_id (str): The ID of the user for whom the verification token is retrieved.

    Returns:
        VerificationToken | None: If a verification token exists for the user, returns the latest
                                  VerificationToken object; otherwise, returns None.
    """
    with Session(engine) as session:
        statement = (
            select(VerificationToken)
            .where(VerificationToken.user_id == user_id)
            .order_by(VerificationToken.created_at.desc())
        )
        verification_token = session.exec(statement).first()
        return verification_token


def verify_user(user_id: str):
    """
    Mark the user with the given ID as verified.

    Parameters:
        user_id (str): The ID of the user to be marked as verified.

    Returns:
        User: The User object after being marked as verified.

    Raises:
        <Any specific exceptions that might occur during the verification process>
    """

    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()
        user.is_verified = True
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def delete_user_verification_tokens(user_id: str):
    """
    Delete all verification tokens associated with the user.

    Parameters:
        user_id (str): The ID of the user for whom the verification tokens will be deleted.

    Raises:
        <Any specific exceptions that might occur during the token deletion process>
    """
    with Session(engine) as session:
        statement = select(VerificationToken).where(
            VerificationToken.user_id == user_id
        )
        verification_tokens = session.exec(statement).all()
        for verification_token in verification_tokens:
            session.delete(verification_token)
        session.commit()
