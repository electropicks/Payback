import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from src import database as db
from src.database import get_db, Transaction, ShoppingTrip, GroupMember, Group, User

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
)


class User(BaseModel):
    userId: str


@router.post("/")
def get_user_groups(user: User):
    """
    Gets all groups that the user is in.
    """
    with db.engine.begin() as connection:
        groups = connection.execute(sqlalchemy.text(
          """
          SELECT groups.id, groups.name FROM groups
          JOIN group_members ON group_members.group_id = groups.id
          JOIN users ON users.id = group_members.user_id AND users.id = :userId
          """
        ), {"userId": int(user.userId)})

    # Convert query results to list of dictionaries as required by the API response format
    json = [{"name": group.name, "groupId": group.id} for group in groups]
    return json


class Group(BaseModel):
    userId: str
    name: str


@router.post("/register")
def create_group(group: Group, db: Session = Depends(get_db)):
    new_group = Group(name=group.name, owner=int(group.userId))
    db.add(new_group)
    db.flush()  # This will assign an ID to new_group without committing the transaction

    new_group_member = GroupMember(group_id=new_group.id, user_id=new_group.owner)
    db.add(new_group_member)

    db.commit()  # Commit both new_group and new_group_member to the database

    return {"group_id": new_group.id}


@router.post("/{group_id}/join")
def join_group(group_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Adds user to group
    """
    new_group_member = GroupMember(group_id=group_id, user_id=user_id)
    db.add(new_group_member)
    db.commit()

    return {"message": "User joined the group successfully."}

@router.get("/{group_id}/transactions")
def list_group_transactions(group_id: int):
    """
    Gets all transactions associated with the group.
    """
    with db.engine.begin() as connection:
        transactions = connection.execute(sqlalchemy.text(
            """
            SELECT *
            FROM transactions
            JOIN transaction_ledger ON transactions.id = transaction_ledger.transaction_id
            WHERE transactions.group_id = :group_id
            """
        ), {"group_id": group_id})


        payload = []
        for transaction in transactions:
            payload.append({
                "transaction_id": transaction.id,
                "from_user_id": transaction.from_id,
                "to_user_id": transaction.to_id,
                "description": transaction.description,
                "date": transaction.timestamp
            })

        return {"transactions": payload}

@router.get("/{group_id}/trips")
def list_group_trips(group_id: int):
    """
    Gets all shopping trips associated with group
    """
    with db.engine.begin() as connection:
        trips = connection.execute(sqlalchemy.text(
            """
            SELECT id, description, created_at
            FROM shopping_trips
            WHERE shopping_trips.group_id = :group_id
            """
        ), {"group_id": group_id})
        payload = []
        for trip in trips:
            amount = connection.execute(sqlalchemy.text(
                """
                SELECT ROUND(SUM(quantity * price)::numeric, 2) FROM line_items
                WHERE line_items.trip_id = :trip_id
                """
            ), {"trip_id": trip.id}).scalar_one()
            payload.append({
                "trip_id": trip.id,
                "amount": amount,
                "description": trip.description,
                "created_at": trip.created_at
            })
        return {"trips": payload}

class Body(BaseModel):
    userId: str
@router.post("/calculate")
def calculate(body: Body):
  with db.engine.begin() as connection:
    res = connection.execute(sqlalchemy.text(
        """
        SELECT line_item_members.user_id, :from_id, SUM(price * quantity) AS amount
        FROM line_items
        JOIN line_item_members ON line_items.id = line_item_members.line_item_id
        GROUP BY line_item_members.user_id
        """
    ), {"from_id": int(body.userId)})
    return [{"userId": row.user_id, "amount": row.amount} for row in res]