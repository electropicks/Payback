import sqlalchemy
import bcrypt
from fastapi import APIRouter

from src import database as db

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register")
def register(username: str, password: str, email: str):
    """
    Create new account
    """
    with db.engine.begin() as connection:
        # check if username is taken
        unqUsername = connection.execute(sqlalchemy.text(
            """
            SELECT * FROM users
            WHERE username = :username
            """),
            {"username": username}
        )
        if unqUsername.rowcount > 0:
            payload = "Username already taken"
            return {
                "message": payload
            }

        salt = bcrypt.gensalt()
        password = password.encode('utf-8')

        user_id = connection.execute(sqlalchemy.text(
            """
            INSERT INTO users (username, password, email)
            VALUES (:username, :password, :email)
            RETURNING id
            """),
            {"username": username, "password": bcrypt.hashpw(password, salt).decode('utf8'), "email": email}
        ).scalar_one()
        connection.execute(sqlalchemy.text(
            """
            INSERT INTO auth_ledger (action, username, email, user_id)
            VALUES (:action, :username, :email, :user_id)
            """),
            {"action": "REGISTER", "username": username, "email": email, "user_id": user_id}
        )
    print(f"New User Registered with id {user_id}")
    payload = "User registered successfully"
    return {
        "message": payload
    }


@router.post("/login")
def login(username: str, password: str):
    """
    Log in with username and password, returns userId
    """

    with db.engine.begin() as connection:
        user = connection.execute(sqlalchemy.text(
            """
            SELECT * FROM users
            WHERE username = :username
            """),
            {"username": username}
        ).first()

        if user is None or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            payload = "Incorrect username or password"
            return {
                "message": payload
            }
        successful = True
        payload = "User logged in successfully"
        userId = user.id
        connection.execute(sqlalchemy.text(
                """
                INSERT INTO auth_ledger (action, username, email, user_id, successful)
                VALUES (:action, :username, :email, :user_id, :successful)
                """),
                {"action": "LOGIN", "username": username, "email": user.email, "user_id": user.id, "successful": successful}
            )
        print(f"User {userId} has signed in")
        
        return {
            "message": payload,
            "userId": userId
        }
