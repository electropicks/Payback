import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src import database as db
from src.util.validation import validate_user, validate_group, validate_transaction

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

    validate_group(group_id)

    with db.engine.begin() as connection:
        group_id = connection.execute(sqlalchemy.text(
            """
            SELECT group_id FROM shopping_trips
            JOIN groups ON shopping_trips.group_id = groups.id
            WHERE shopping_trips.id = :trip_id
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
        ), {"transaction_id": transaction_id, "from_id": newT.from_id, "to_id": newT.to_id, "amount":newT.amount * 100})
        return {"transactionId" : transaction_id}
    raise HTTPException(status_code=400, detail="Failed")

@router.post("/delete/{transaction_id}")
def delete_transaction(transaction_id: int):
    """
    Deletes transaction from ledger by inserting inverse 
    """

    validate_transaction(transaction_id)

    with db.engine.begin() as connection:
        transaction = connection.execute(sqlalchemy.text(
            """
            SELECT to_id, from_id, change, group_id, trip_id
            FROM transactions
            JOIN transaction_ledger ON transaction_ledger.transaction_id = transactions.id
            WHERE transactions.id = :transaction_id
            """
        ), {"transaction_id": transaction_id})
        ids = connection.execute(sqlalchemy.text("""
            SELECT trip_id, group_id
            FROM transactions
            JOIN transaction_ledger ON transaction_ledger.transaction_id = transactions.id
            WHERE transactions.id = :transaction_id
            LIMIT 1
        """), {"transaction_id": transaction_id}).first()

        new_id = connection.execute(sqlalchemy.text(
            """
            INSERT INTO transactions (description, trip_id, group_id)
            VALUES (:desc, :trip, :group)
            RETURNING id
            """
        ), {"desc": "Reverted transaction", "trip": ids.trip_id, "group": ids.group_id}).scalar_one()
        for row in transaction:
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO transaction_ledger (to_id, from_id, change, transaction_id)
                VALUES (:to_id, :from_id, :change, :transaction_id)
                RETURNING id
                """
            ), {"to_id": row.to_id,
                "from_id": row.from_id,
                "transaction_id": new_id,
                "change": -row.change}).scalar_one()
        print(f"{transaction_id} has been deleted")
        return {"newId": new_id}
    raise HTTPException(status_code=400, detail="Failed")
