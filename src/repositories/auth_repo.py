from sqlmodel import Session, select
from db.models.verification_token import VerificationToken

from db.models.user import User
from db.engine import engine


def check_user_exists_with_email(email: str):
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        return user


def create_user_with_google(
    sub: str, given_name: str, family_name: str, email: str, email_verified: bool
):
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
    with Session(engine) as session:
        verification_token = VerificationToken(user_id=user_id)
        session.add(verification_token)
        session.commit()
        session.refresh(verification_token)
        return verification_token


def get_latest_verification_token(user_id: str):
    with Session(engine) as session:
        statement = (
            select(VerificationToken)
            .where(VerificationToken.user_id == user_id)
            .order_by(VerificationToken.created_at.desc())
        )
        verification_token = session.exec(statement).first()
        return verification_token


def verify_user(user_id: str):
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()
        user.is_verified = True
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def delete_user_verification_tokens(user_id: str):
    with Session(engine) as session:
        statement = select(VerificationToken).where(
            VerificationToken.user_id == user_id
        )
        verification_tokens = session.exec(statement).all()
        for verification_token in verification_tokens:
            session.delete(verification_token)
        session.commit()
