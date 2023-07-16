from pydantic import BaseModel


class JSONTokens(BaseModel):
    access_token: str
    refresh_token: str


class Ok(BaseModel):
    ok: bool
