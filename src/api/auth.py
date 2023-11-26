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
        connection.execute(db.users.insert().values(username=username, password=password, email=email))

    payload = "User registered successfully"
    return {
        "message": payload
    }

@router.post("/login")
def login(username: str, password: str):
    """"""

    with db.engine.begin() as connection:
        result = connection.execute(db.users.select().where(db.users.c.username == username))

    for row in result:
        if row.password == password:
            payload = "User logged in successfully"
        else:
            payload = "Incorrect password"

    return {
        "message": payload
    }
