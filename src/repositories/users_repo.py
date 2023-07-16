from sqlmodel import Session, select

from db.models.user import User
from db.engine import engine


def create_user(email: str, password: str):
    user = User(email=email, password=password)
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def get_user_by_email(email: str):
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        return user


def get_user_by_id(user_id: str):
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()
        return user
