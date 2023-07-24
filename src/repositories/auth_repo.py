from sqlmodel import Session, select
from db.engine import engine
from db.models.user import User


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
