from fastapi import FastAPI
from src.routers import users_router as users, auth_router as auth
from src.utils.auth_utils import send_email

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])


@app.get("/health")
async def root():
    return {"ok": True}


@app.get("/test")
async def test():
    return await send_email("lemjuidump+test@gmail.com", "312321")
