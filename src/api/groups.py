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
    """"""
    new_group_member = GroupMember(group_id=group_id, user_id=user_id)
    db.add(new_group_member)
    db.commit()

    return {"message": "User joined the group successfully."}

@router.get("/{group_id}/transactions")
def list_group_transactions(group_id: int):
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

class newTransaction(BaseModel):
    trip_id: int
    from_id: int
    to_id: int
    amount: float
    description: str

@router.post("/{group_id}/transactions")
def add_transactions(newT: newTransaction, group_id: int):
    with db.engine.begin() as connection:
        transaction_id = connection.execute(sqlalchemy.text(
            """
            INSERT INTO transactions (description, trip_id, group_id)
            VALUES (:desc, :trip, :group_id)
            RETURNING id
            """
        ), {"desc": newT.description, "trip": newT.trip_id, "group_id": group_id}).scalar_one()
        connection.execute(sqlalchemy.text(
            """
            INSERT INTO transaction_ledger (transaction_id, to_id, from_id, change)
            VALUES (:transaction_id, :to_id, :from_id, :amount)
            """
        ), {"transaction_id": transaction_id, "from_id": newT.from_id, "to_id": newT.to_id, "amount":newT.amount})
    return "OK"

@router.get("/{group_id}/trips")
def list_group_trips(group_id: int):
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



class Transaction(BaseModel):
    transaction_id: str

@router.post("/{group_id}/trips/{trip_id}/delete")
def delete_transaction(transaction_id: Transaction, group_id: int, trip_id: int):
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            """
            DELETE FROM transactions
            WHERE id = :id
            """
        ), {"id": transaction_id})
        return "OK"

class Trip(BaseModel):
    userId: str
    description: str

@router.post("/{group_id}/trips")
def create_trip(group_id: int, trip: Trip):
    with db.engine.begin() as connection:
        trip_id = connection.execute(sqlalchemy.text(
            """
            INSERT INTO shopping_trips (description, payer_id, group_id)
            VALUES (:desc, :payer, :group)
            RETURNING id
            """
        ), {"desc": trip.description, "payer": trip.userId, "group": group_id}).scalar_one()
        return {"tripId": trip_id}

@router.get("/{group_id}/trips/{trip_id}")
def get_trip(group_id: int, trip_id: int):
    with db.engine.begin() as connection:
        trip = connection.execute(sqlalchemy.text(
            """
            SELECT description, created_at
            FROM shopping_trips
            WHERE shopping_trips.id = :trip_id
            """
        ), {"group_id": group_id, "trip_id": trip_id}).first()
        amount = connection.execute(sqlalchemy.text(
            """
            SELECT ROUND(SUM(quantity * price)::numeric, 2) FROM line_items
            WHERE line_items.trip_id = :trip_id
            """
        ), {"trip_id": trip_id}).scalar_one()
        return {
            "description": trip.description,
            "amount": amount,
            "createdAt": trip.created_at
        }

@router.get("/{group_id}/trips/{trip_id}/items")
def get_trip_items(group_id: int, trip_id: int):
    with db.engine.begin() as connection:
        returnBody = []
        items = connection.execute(sqlalchemy.text(
            """
            SELECT item_name, price, quantity
            FROM shopping_trips
            JOIN line_items ON shopping_trips.id = line_items.trip_id
            WHERE shopping_trips.id = :trip_id
            AND group_id = :group_id
            """
        ), {"group_id": group_id, "trip_id": trip_id}).all()
        for item in items:
            returnBody.append(
                {
                    "Item Name" : item.item_name,
                    "Price" : item.price,
                    "Quanity" : item.quantity
                }
            )
        return returnBody

class Item(BaseModel):
    name: str
    price: float
    quantity: int
    optedOut: List[int]
class AddLineItem(BaseModel):
    userId: str
    items: List[Item]

@router.post("/{group_id}/trips/{trip_id}/add")
def add_line_item(body: AddLineItem, group_id: int, trip_id: int):
    with db.engine.begin() as connection:
        for item in body.items:
            line_item_id = connection.execute(sqlalchemy.text(
                """
                INSERT INTO line_items (item_name, price, quantity, trip_id)
                VALUES (:name, :price, :quantity, :trip_id)
                RETURNING id
                """
            ), {"name": item.name, "price": item.price, "quantity": item.quantity, "trip_id": trip_id}).scalar_one()
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO line_item_members (user_id, line_item_id)
                SELECT user_id, :line_item_id FROM group_members
                WHERE (user_id != ANY(:optout)
                OR :optout is null)
                AND group_id = :group_id
                """
            ), {"line_item_id": line_item_id, "optout": item.optedOut or None, "group_id": group_id})

        transaction_id = connection.execute(sqlalchemy.text(
            """
            INSERT INTO transactions (description, trip_id, group_id)
            VALUES (:desc, :trip, :group_id)
            RETURNING id
            """
        ), {"desc": "Paid for trip", "trip": trip_id, "group_id": group_id}).scalar_one()

        connection.execute(sqlalchemy.text(
            """
            INSERT INTO transaction_ledger
            (transaction_id, to_id, from_id, change)
              SELECT :transaction_id, line_item_members.user_id, :from_id, SUM(price * quantity) AS amount
              FROM line_items
              JOIN line_item_members ON line_items.id = line_item_members.line_item_id
              GROUP BY line_item_members.user_id
            """
        ), {"transaction_id": transaction_id, "from_id": int(body.userId)})
        return "OK"

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