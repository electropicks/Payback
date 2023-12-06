import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src import database as db
from src.util.validation import validate_user, validate_group, validate_trip, validate_user_in_group

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
)


@router.get("/{userId}")
def get_user_groups(userId: int):
    """
    Gets all groups that the user is in.
    """

    validate_user(userId)

    with db.engine.begin() as connection:
        groups = connection.execute(sqlalchemy.text(
          """
          SELECT groups.id, groups.name 
          FROM groups
          JOIN group_members ON group_members.group_id = groups.id
          WHERE user_id = :userId
          """
        ), {"userId": userId})
    
        print(f"{userId} requested all the groups they are in")

        # Convert query results to list of dictionaries as required by the API response format
        json = [{"name": group.name, "groupId": group.id} for group in groups]
        return json

    raise HTTPException(status_code=400, detail="Failed")


class Group(BaseModel):
    userId: int
    name: str

@router.post("/register")
def create_group(group: Group):
  
    validate_user(group.userId)

    with db.engine.begin() as connection:

        group_id = connection.execute(sqlalchemy.text(
            """
            INSERT INTO groups (name, owner)
            VALUES (:name, :owner)
            RETURNING id
            """
        ), {"name": group.name, "owner": group.userId}).scalar_one()

        connection.execute(sqlalchemy.text(
            """
            INSERT INTO group_members (group_id, user_id)
            VALUES (:group_id, :user_id)
            """
        ), {"group_id": group_id, "user_id": group.userId})
    
        print(f"{group.userId} has created a group with id {group_id}")

        return {"group_id": group_id}

    raise HTTPException(status_code=400, detail="Failed")


@router.post("/{group_id}/join")
def join_group(group_id: int, user_id: int):
    """
    Adds user to group
    """
    validate_user(user_id)
    validate_group(group_id)

    with db.engine.begin() as connection:
        inGroup = connection.execute(sqlalchemy.text(
            """
            SELECT user_id
            FROM group_members
            WHERE user_id = :user_id AND group_id = :group_id
            """
        ), {"user_id" : user_id, "group_id" : group_id}).first()
        if inGroup:
            raise HTTPException(status_code=400, detail="Already in group.")
        connection.execute(sqlalchemy.text(
            """
            INSERT INTO group_members (group_id, user_id)
            VALUES (:group_id, :user_id)
            """
        ), {"group_id" : group_id, "user_id": user_id})
        print(f"{user_id} has joined group {group_id}")
        return {"message": "Joined group successfully."}
    raise HTTPException(status_code=400, detail="Failed")


@router.get("/{group_id}/transactions")
def list_group_transactions(group_id: int):
    """
    Gets all transactions associated with the group.
    """

    validate_group(group_id)

    with db.engine.begin() as connection:
        transactions = connection.execute(sqlalchemy.text(
            """
            SELECT *
            FROM transactions
            JOIN transaction_ledger ON transactions.id = transaction_ledger.transaction_id
            WHERE transactions.group_id = :group_id
            """
        ), {"group_id": group_id})

        payload = [
            {
                "transaction_id": transaction.id,
                "from_user_id": transaction.from_id,
                "to_user_id": transaction.to_id,
                "description": transaction.description,
                "date": transaction.timestamp
            }
            for transaction in transactions
        ]
        print(f"Retreieved all transactions for {group_id}")
        return {"transactions": payload}
    raise HTTPException(status_code=400, detail="Failed")

@router.get("/{group_id}/trips")
def list_group_trips(group_id: int):
    """
    Gets all shopping trips associated with group
    """

    validate_group(group_id)

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
                "amount": amount / 100,
                "description": trip.description,
                "created_at": trip.created_at
            })
        print(f"Retreieved all trips for {group_id}")

        return {"trips": payload}
    raise HTTPException(status_code=400, detail="Failed")


@router.post("/calculate")
def calculate(user_id: int, group_id: int):
    """
    Calculate how much user owes each group member and how much
    they are owed by other group members
    """

    validate_user_in_group(user_id, group_id)

    with db.engine.begin() as connection:
        usersOwed = connection.execute(sqlalchemy.text(
            """
            WITH paid_balance AS (
            SELECT user_id,
                SUM(CASE WHEN from_id = :user_id AND to_id = user_id THEN change ELSE 0 END) AS amount_paid,
                SUM(CASE WHEN to_id = :user_id AND from_id = user_id THEN change ELSE 0 END) AS amount_owed
            FROM transaction_ledger
            JOIN transactions ON transaction_id = transactions.id
            JOIN group_members ON transactions.group_id = group_members.group_id
            WHERE (from_id = :user_id OR to_id = :user_id) AND transactions.group_id = :group_id
            GROUP BY user_id
            )
            SELECT user_id, SUM(amount_owed - amount_paid)/100 AS balance
            FROM paid_balance
            WHERE user_id != :user_id
            GROUP BY user_id
            """
        ), {"user_id": user_id, "group_id": group_id})
        print(f"Calculated expenses for {group_id}")

    return [{"userId": row.user_id, "amount": row.balance / 100} for row in usersOwed]

@router.post("{group_id}/search")
def search_line_items(group_id: int, query: str):
    """
    Searches for line items in the group's shopping trips
    """
    validate_group(group_id)

    with db.engine.begin() as connection:
        line_items = connection.execute(sqlalchemy.text(
            """
            SELECT line_items.id, line_items.quantity, line_items.price, line_items.item_name, shopping_trips.id AS trip_id, shopping_trips.description AS trip_description
            FROM line_items
            JOIN shopping_trips ON line_items.trip_id = shopping_trips.id
            WHERE shopping_trips.group_id = :group_id AND line_items.item_name ILIKE :query
            """
        ), {"group_id": group_id, "query": f"%{query}%"}).fetchall()
        return [{"lineItemId": row.id, "quantity": row.quantity, "price": row.price / 100, "item_name": row.item_name, "tripId": row.trip_id, "tripDescription": row.trip_description} for row in line_items]
    raise HTTPException(status_code=400, detail="Failed")
        
