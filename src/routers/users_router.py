"""
User Router Module.

This module defines the API router for user-related endpoints. It includes a single endpoint
to get the current authenticated user's information.

Module Dependencies:
    - fastapi: A web framework for building APIs.
    - db.models.user.User: The User model class representing users in the database.
    - src.dependencies.get_current_active_user: A dependency function to retrieve the currently
      authenticated and active user.

Functions:
    get_current_user: Endpoint to get the current authenticated user's information.

"""


from fastapi import APIRouter, Depends

from db.models.user import User
from src.dependencies import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=User, response_model_exclude=["password", "disabled"])
async def get_current_user(
    user: User = Depends(get_current_active_user),
):
    """
    Endpoint to get the current authenticated user's information.

    Parameters:
        user (User): The currently authenticated and active user.

    Returns:
        User: The user's information, excluding the password and disabled status.

    Raises:
        HTTPException: If the user is not authenticated or is disabled.

    """
    return user
