import sqlalchemy
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from src import database as db
from src.util.validation import validate_trip, validate_user_in_group, validate_item_in_trip
 
router = APIRouter(
    prefix="/trips",
    tags=["trips"],
)

@router.get("/{trip_id}")
def get_trip(trip_id: int):
    """
    Gets the metadata of a certain trip
    """

    validate_trip(trip_id)

    with db.engine.begin() as connection:
        trip = connection.execute(sqlalchemy.text(
            """
            SELECT description, created_at
            FROM shopping_trips
            WHERE shopping_trips.id = :trip_id
            """
        ), {"trip_id": trip_id}).first()
        amount = connection.execute(sqlalchemy.text(
            """
            SELECT ROUND(SUM(quantity * price)::numeric, 2) FROM line_items
            WHERE line_items.trip_id = :trip_id
            """
        ), {"trip_id": trip_id}).scalar_one()
        print(f"Retrieved info for {trip_id}")
        return {
            "description": trip.description,
            "amount": amount / 100 if amount else 0,
            "createdAt": trip.created_at
        }
    raise HTTPException(status_code=400, detail="Failed")

class Trip(BaseModel):
    userId: int
    groupId: int
    description: str

@router.post("/create")
def create_trip(trip: Trip):
    """
    Creates a new shopping trip
    """
    
    validate_user_in_group(trip.userId, trip.groupId)

    with db.engine.begin() as connection:
        trip_id = connection.execute(sqlalchemy.text(
            """
            INSERT INTO shopping_trips (description, payer_id, group_id)
            VALUES (:desc, :payer, :group)
            RETURNING id
            """
        ), {"desc": trip.description, "payer": trip.userId, "group": trip.groupId}).scalar_one()
        print(f"Created trip with id {trip_id}")
        return {"tripId": trip_id}
    raise HTTPException(status_code=400, detail="Failed")

@router.get("{trip_id}/items")
def trip_items(trip_id: int):
    """
    Retrieves all the items from a trip
    """

    validate_trip(trip_id)
    group_id = get_trip_group(trip_id)

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
                    "Price" : item.price / 100,
                    "Quanity" : item.quantity
                }
            )
        print(f"Retreieved trip items for trip {trip_id}")
        return returnBody
    raise HTTPException(status_code=400, detail="Failed")

class Item(BaseModel):
    name: str
    price: float
    quantity: int
    optedOut: List[int]
class AddLineItem(BaseModel):
    userId: int
    items: List[Item]

@router.post("/{trip_id}/addItems")
def add_line_items(body: AddLineItem, trip_id: int):
    """
    Adds a list of items to the shopping trip.
    """
    validate_trip(trip_id)
    group_id = get_trip_group(trip_id)
    validate_user_in_group(body.userId, group_id)

    validated_users = set()
    validated_users.add(body.userId)

    with db.engine.begin() as connection:
        for item in body.items:
            line_item_id = connection.execute(sqlalchemy.text(
                """
                INSERT INTO line_items (item_name, price, quantity, trip_id)
                VALUES (:name, :price, :quantity, :trip_id)
                RETURNING id
                """
            ), {"name": item.name, "price": item.price * 100, "quantity": item.quantity, "trip_id": trip_id}).scalar_one()
            for user in item.optedOut:
                if user not in validated_users:
                    validate_user_in_group(user, group_id)
                    validated_users.add(user)
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO line_item_members (user_id, line_item_id)
                SELECT user_id, :line_item_id FROM group_members
                WHERE (user_id <> ALL(:optout)
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
            WITH T1 AS(
              SELECT line_item_id, COUNT(DISTINCT line_item_members.user_id) cnt
              FROM line_items
              JOIN line_item_members ON line_items.id = line_item_members.line_item_id
              JOIN group_members ON line_item_members.user_id = group_members.user_id
              WHERE group_members.group_id = :group_id
              GROUP BY line_item_id
            )
            INSERT INTO transaction_ledger
            (transaction_id, to_id, from_id, change)
              SELECT :transaction_id, line_item_members.user_id, :from_id, SUM((price * quantity)/cnt) AS amount
              FROM line_items
              JOIN line_item_members ON line_items.id = line_item_members.line_item_id
              JOIN group_members ON line_item_members.user_id = group_members.user_id
              JOIN T1 ON T1.line_item_id = line_items.id
              WHERE group_members.group_id = :group_id
              GROUP BY line_item_members.user_id
            """
        ), {"transaction_id": transaction_id, "from_id": body.userId, "group_id": group_id})
        print(f"Added trip items to trip {trip_id}")
        return "OK"
    raise HTTPException(status_code=400, detail="Failed")

@router.post("/{trip_id}/update_item_price")
def update_item_price(trip_id: int, item_id: int, price: float):
    """
    Updates price for an item in a trip
    """

    if price < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative")

    validate_item_in_trip(item_id, trip_id)

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            """
            UPDATE line_items
            SET price = :price
            WHERE id = :item_id
            AND trip_id = :trip_id
            """
        ), {"price": price * 100, "item_id": item_id, "trip_id": trip_id})
        print(f"Updated id for item {item_id} in {trip_id}")
        return "OK"
    raise HTTPException(status_code=400, detail="Failed")

@router.post("{trip_id}/search")
def search_line_items_by_trip(trip_id: int, query: str):
    """
    Searches for line items in the group's shopping trips
    """

    validate_trip(trip_id)

    with db.engine.begin() as connection:
        line_items = connection.execute(sqlalchemy.text(
            """
            SELECT line_items.id, line_items.quantity, line_items.price, line_items.item_name, shopping_trips.description AS trip_description
            FROM line_items
            JOIN shopping_trips ON line_items.trip_id = shopping_trips.id
            WHERE shopping_trips.id = :trip_id AND line_items.item_name ILIKE :query
            """
        ), {"trip_id": trip_id, "query": f"%{query}%"}).fetchall()
        return [{"lineItemId": row.id, "quantity": row.quantity, "price": row.price / 100, "item_name": row.item_name, "tripDescription": row.trip_description} for row in line_items]
    raise HTTPException(status_code=400, detail="Failed")

def get_trip_group(trip_id: int):
    """
    Returns groupId from tripId
    """
    with db.engine.begin() as connection:
        group_id = connection.execute(sqlalchemy.text(
            """
            SELECT group_id
            FROM shopping_trips
            WHERE id = :trip_id
            """
        ), {"trip_id": trip_id}).scalar_one()

        return group_id