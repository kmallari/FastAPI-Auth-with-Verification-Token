from sqlmodel import SQLModel
from .models import user, verification_token
from .engine import engine

SQLModel.metadata.create_all(engine)
