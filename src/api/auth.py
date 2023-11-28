import sqlalchemy
from fastapi import APIRouter

from src import database as db

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register")
def register(username: str, password: str, email: str):
    """"""
    with db.engine.begin() as connection:
        # check if username is taken
        result = connection.execute(sqlalchemy.text(
            """
            SELECT * FROM users
            WHERE username = :username
            """),
            {"username": username}
        )
        if result.rowcount > 0:
            payload = "Username already taken"
            return {
                "message": payload
            }
        insert_result = connection.execute(sqlalchemy.text(
            """
            INSERT INTO users (username, password, email)
            VALUES (:username, :password, :email)
            RETURNING id
            """),
            {"username": username, "password": password, "email": email}
        )
        user_id = insert_result.first()[0]
        connection.execute(sqlalchemy.text(
            """
            INSERT INTO auth_ledger (action, username, email, user_id)
            VALUES (:action, :username, :email, :user_id)
            """),
            {"action": "REGISTER", "username": username, "email": email, "user_id": user_id}
        )

    payload = "User registered successfully"
    return {
        "message": payload
    }


@router.post("/login")
def login(username: str, password: str):
    """"""

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            SELECT * FROM users
            WHERE username = :username
            """),
            {"username": username}
        ).first()
        if result is None:
            payload = "Incorrect username"
            return {
                "message": payload
            }
        if result.password == password:
            successful = True
            payload = "User logged in successfully"
        else:
            successful = False
            payload = "Incorrect password"
        connection.execute(sqlalchemy.text(
                """
                INSERT INTO auth_ledger (action, username, email, user_id, successful)
                VALUES (:action, :username, :email, :user_id, :successful)
                """),
                {"action": "LOGIN", "username": username, "email": result.email, "user_id": result.id, "successful": successful}
            )
        
    return {
        "message": payload
    }
