"""
This script defines two Pydantic models: JSONTokens and Ok.

Contents:
- JSONTokens: A response model representing a JSON object with access_token and refresh_token
    attributes.
- Ok: A response model representing a JSON object with a single boolean field 'ok', indicating
    the success or status of an operation.
"""

from pydantic import BaseModel


class JSONTokens(BaseModel):
    access_token: str
    refresh_token: str


class Ok(BaseModel):
    ok: bool
