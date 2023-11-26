import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from fastapi.responses import JSONResponse

from src import database as db
from src.database import get_db, Transaction, ShoppingTrip, GroupMember, Group, User

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)

class Transaction(BaseModel):
    trip_id: int
    from_id: int
    to_id: int
    amount: float
    description: str

@router.post("/add")
def add_transaction(newT: Transaction, group_id: int):
    """
    Adds a transaction to the trip.
    Finds groupId from tripId.
    """
    with db.engine.begin() as connection:
        group_id = connection.execute(sqlalchemy.text(
            """
            SELECT group_id FROM trips
            JOIN groups ON trips.group_id = groups.id
            WHERE trip_id = :trip_id
            """
        ), {"trip_id": newT.trip_id}).scalar_one()
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

@router.post("/{trip_id}/delete")
def delete_transaction(transaction_id: Transaction):
    """
    Deletes transaction from ledger and inserts inverse 
    """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            """
            DELETE FROM transactions
            WHERE id = :id
            """
        ), {"id": transaction_id})
        
    return "OK"