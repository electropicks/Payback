import sqlalchemy
from fastapi.testclient import TestClient

from server import app
from src import database as db

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Get PAYBACK"}


def test_get_user_groups():
    response = client.post("/groups/", json={"userId": 1, "name": "Test Group"})
    assert response.status_code == 200
    assert response.json() == [
        {'groupId': 1,
         'name': 'originGroup'},
        {'groupId': 2,
         'name': 'The Second Group'},
        {'groupId': 3,
         'name': 'Test Group'},
    ]


def test_create_group():
    with db.engine.begin() as connection:
        last_group_id = connection.execute(sqlalchemy.text(
            """
            SELECT MAX(id)
            FROM groups
            """
        )).scalar_one()
    response = client.post("/groups/register", json={"userId": 1, "name": "Test Group"})
    assert response.status_code == 200
    assert response.json()['group_id'] > last_group_id
    with db.engine.begin() as connection:
        print("deleting test group")
        connection.execute(sqlalchemy.text(
            """
            DELETE FROM groups
            WHERE id = :group_id
            """
        ), {"group_id": response.json()['group_id']})


def test_join_group():
    response = client.post("/groups/1/join", json={"userId": 1})
    print("response", response)
    assert response.status_code == 200
    assert response.json() == {"message": "Joined group successfully."}
