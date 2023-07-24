"""
Run to delete all tables and data.
"""

from sqlmodel import SQLModel
from .models import user, verification_token
from .engine import engine

SQLModel.metadata.drop_all(engine)
