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

from src.routers import users_router as users, auth_router as auth

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])


@app.get("/health")
async def root():
    """
    Health check endpoint.

    Returns:
        dict: A dictionary with the "ok" key set to True, indicating the application is healthy.
    """
    return {"ok": True}
