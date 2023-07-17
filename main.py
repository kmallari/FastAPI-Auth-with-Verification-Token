from fastapi import FastAPI
from src.routers import users_router as users


app = FastAPI()


app.include_router(users.router, prefix="/users", tags=["users"])


@app.get("/health")
async def root():
    return {"ok": True}
