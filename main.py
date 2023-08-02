"""
This script initializes a FastAPI application and configures the main routers for users
    and authentication.

Contents:
- FastAPI app object
- Users router
- Authentication router

Additionally, it includes a health check endpoint:

- /health: A health check endpoint that returns a JSON response with the "ok" key set to True,
indicating that the application is healthy.

"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import users_router as users, auth_router as auth
from src.routers.auth_router import oauth2_scheme

from fastapi import Depends

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])

origins = [
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """
    Health check endpoint.

    Returns:
        dict: A dictionary with the "ok" key set to True, indicating the application is healthy.
    """
    return {"ok": True}


@app.get("/protected")
async def protected(token: str = Depends(oauth2_scheme)):
    return {"token": token}
