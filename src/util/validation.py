import sqlalchemy
from fastapi import HTTPException

from src import database as db

def validate_user(userId):
    with db.engine.begin() as connection:
        validUser = connection.execute(sqlalchemy.text(
            """
            SELECT id
            FROM users
            WHERE id = :user_id
            """
        ), {"user_id" : userId}).first()
        if validUser is None:
            print("Invalid User ID")
            raise HTTPException(status_code=400, detail="Invalid userId")


def validate_group(groupId):
    with db.engine.begin() as connection:
        validGroup = connection.execute(sqlalchemy.text(
            """
            SELECT id
            FROM groups
            WHERE id = :group_id
            """
        ), {"group_id" : groupId}).first()
        if validGroup is None:
            print("Invalid group ID")
            raise HTTPException(status_code=400, detail="Invalid groupId")

def validate_transaction(transactionId):
    with db.engine.begin() as connection:
        validTransaction = connection.execute(sqlalchemy.text(
            """
            SELECT id FROM transactions
            WHERE id = :id
            """
        ), {"id": transactionId}).first()

        if validTransaction is None:
            print("Invalid Transaction ID")
            raise HTTPException(status_code=400, detail="Invalid transaction ID")

def validate_trip(tripId):
    with db.engine.begin() as connection:
        validTrip = connection.execute(sqlalchemy.text(
          """
          SELECT * FROM shopping_trips
          WHERE id = :id
          """
        ), {"id": tripId})
        if validTrip is None:
            raise HTTPException(status_code=400, detail="Invalid trip ID")