from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
    dependencies=[Depends(auth.get_api_key)],
)

class User(BaseModel):
  userId: str
@router.post("/")
def getUserGroups(user: User):
  """
  Gets all groups that user is in.
  """
  with db.engine.begin() as connection:
    groups = connection.execute(sqlalchemy.text(
      """
      SELECT groups.name FROM groups
      JOIN group_members ON group_members.group_id = groups.id
      JOIN users ON users.id = group_members.user_id AND users.id = :userId
      """
    ), {"userId": int(user.userId)})
    json = [{"name": group.name} for group in groups]
    return json

class Group(BaseModel):
  userId: str
  name: str
@router.post("/create")
def createGroup(group: Group):
  with db.engine.begin() as connection:
    groupId = connection.execute(sqlalchemy.text(
      """
      INSERT INTO groups (name, owner)
      VALUES (:name, :owner)
      RETURNING id
      """
    ), {"name": group.name, "owner": int(group.userId)}).scalar_one()

    connection.execute(sqlalchemy.text(
      """
      INSERT INTO group_members (group_id, user_id)
      VALUES (:groupId, :ownerId)
      """
    ), {"groupId": groupId, "ownerId": group.userId})

    return {"group_id": groupId}