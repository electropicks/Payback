import sqlalchemy
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from src import database as db
from src.util.validation import validate_user, validate_group, validate_trip
 
router = APIRouter(
    prefix="/trips",
    tags=["trips"],
)

@router.get("/{trip_id}")
def get_trip(trip_id: int):
    """
    Gets the metadata of a certain trip
    """
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
            "amount": amount / 100,
            "createdAt": trip.created_at
        }
    raise HTTPException(status_code=400, detail="Failed")

class Trip(BaseModel):
    userId: int
    tripId: int | None = None
    groupId: int
    description: str | None = None

@router.post("/create")
def create_trip(trip: Trip):
    """
    Creates a new shopping trip
    """
    
    validate_group(trip.groupId)

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

@router.post("/items")
def trip_items(trip: Trip):
    """
    Retrieves all the items from a trip
    """

    validate_group(trip.groupId)
    validate_trip(trip.tripId)

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
        ), {"group_id": trip.groupId, "trip_id": trip.tripId}).all()
        for item in items:
            returnBody.append(
                {
                    "Item Name" : item.item_name,
                    "Price" : item.price / 100,
                    "Quanity" : item.quantity
                }
            )
        print(f"Retreieved trip items for trip {trip.tripId}")
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
def add_line_items(body: AddLineItem, group_id: int, trip_id: int):
    """
    Adds a list of items to the shopping trip.
    """

    validate_group(group_id)
    validate_trip(trip_id)

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

        group_id = connection.execute(sqlalchemy.text(
            """
            SELECT group_id FROM shopping_trips
            WHERE id = :trip_id
            """
        ), {"trip_id": trip_id}).scalar_one()

        connection.execute(sqlalchemy.text(
            """
            INSERT INTO transaction_ledger
            (transaction_id, to_id, from_id, change)
              SELECT :transaction_id, line_item_members.user_id, :from_id, SUM(price * 100 * quantity) AS amount
              FROM line_items
              JOIN line_item_members ON line_items.id = line_item_members.line_item_id
              JOIN group_members ON line_item_members.user_id = group_members.user_id
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
    with db.engine.connect.execution_options(isolation_level="SERIALIZABLE") as conn:
        with conn.begin() as connection:
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