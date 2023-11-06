import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src import database as db
from src.database import get_db, Transaction, GroupMember

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
)


class User(BaseModel):
    userId: str


@router.post("/")
def get_user_groups(user: User, db: Session = Depends(get_db)):
    """
    Gets all groups that the user is in.
    """
    # Assuming 'User' model has a relationship 'group_memberships' to 'GroupMember' model
    # and 'GroupMember' model has a 'group' relationship to 'Group' model
    user_groups = (
        db.query(Group.name)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .join(User, User.id == GroupMember.user_id)
        .filter(User.id == int(user.userId))
        .all()
    )

    # Convert query results to list of dictionaries as required by the API response format
    json = [{"name": group.name} for group in user_groups]
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
def list_group_transactions(group_id: int, user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).filter(Transaction.group_id == group_id).all()
    payload = []
    for transaction in transactions:
        payload.append({
            "transaction_id": transaction.id,
            "from_user_id": transaction.from_user_id,
            "to_user_id": transaction.to_user_id,
            "amount": transaction.amount,
            "description": transaction.description,
            "date": transaction.date
        })
    return {"transactions": payload}
