from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from src.database import get_db, User
from src.supabase_client import supabase

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

# Define an OAuth2PasswordBearer for token validation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/signin")
def signin(db: Session = Depends(get_db)):
    """
    Signs in user with Google OAuth.
    """
    # You may want to include OAuth flow logic here, but for simplicity, let's use a mock response.
    # Replace this with your actual OAuth authentication logic.

    # Mocking a successful OAuth response
    mock_oauth_response = {
        "access_token": "your_access_token",
        "token_type": "bearer"
    }

    # Assuming you have a function to create or retrieve a user from the database.
    # Replace this with your actual logic.
    url = create_or_get_user(db)
    # print(user.email)

    # user_data = User(email=user.email);
    # Return the mock OAuth response
    return RedirectResponse(url)


def create_or_get_user(db: Session = Depends(get_db)):
    # Implement your user creation or retrieval logic here.
    # You may want to check if the user already exists in the database based on their email or other unique identifier.
    # If the user exists, return the existing user; otherwise, create a new user and return it.
    # This function should handle the interaction with your database and user management logic.

    # Create a new user
    print("Creating new user")
    res = supabase.auth.sign_in_with_oauth({"provider": "google"})
    print(res)
    test = RedirectResponse(res.url, status_code=303)
    print(test)

    return res.url
