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
        ), {"id": tripId}).first()
        if validTrip is None:
            raise HTTPException(status_code=400, detail="Invalid trip ID")

def validate_user_in_group(userId, groupId):
    validate_user(userId)
    validate_group(groupId)
    with db.engine.begin() as connection:
        userInGroup = connection.execute(sqlalchemy.text(
            """
            SELECT * FROM group_members
            WHERE group_id = :groupId AND user_id = :userId
            """
        ), {"userId": userId, "groupId": groupId}).first()
        if userInGroup is None:
            raise HTTPException(status_code=400, detail=f"User {userId} is not in group")

def validate_item_in_trip(tripId, itemId):
    validate_trip(tripId)
    with db.engine.begin() as connection:
        itemInTrip = connection.execute(sqlalchemy.text(
            """
            SELECT * FROM line_items
            WHERE line_items.id = :itemId AND trip_id = :tripId
            """
        ), {"itemId": itemId, "tripId": tripId}).first()
        if itemInTrip is None:
            raise HTTPException(status_code=400, detail=f"Item {itemId} is not in trip")
        