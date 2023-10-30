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
  email: str
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
      JOIN users ON users.id = group_members.user_id
      """
    ))
    json = [{"name": group.name} for group in groups]
    return json