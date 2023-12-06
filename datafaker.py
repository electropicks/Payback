#line_item_members: 529,800
#line_items: 132,450
#transactions: 132,450
#transactions_ledger: 132,450
#shopping_trips: 13,245
#group_members: 26,490
#users: 26,490
#groups: 6,623

import sqlalchemy
import os
import dotenv
from faker import Faker
import numpy as np

def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

engine = sqlalchemy.create_engine(database_connection_url())

with engine.begin() as conn:
        conn.execute(sqlalchemy.text("""
            TRUNCATE TABLE auth_ledger, group_members, groups, line_item_members, line_items, shopping_trips, transaction_ledger, transactions, users RESTART IDENTITY CASCADE;
    """))
        
num_users = 36000
fake = Faker()

with engine.begin() as conn:
    users = []
    for i in range(num_users):
        if i % 10 == 0:
          print(f"User Created {i}")
        profile = fake.profile()
        email = fake.unique.email()
        users.append({
            "username": profile['name'],
            "password": fake.password(),
            "created_at": fake.date_time_between(start_date='-5y', end_date='now', tzinfo=None),
            "email": email
        })

    conn.execute(sqlalchemy.text("""
        INSERT INTO users (username, password, created_at, email)
        VALUES (:username, :password, :created_at, :email)
    """), users)

    # create da groups, insert owner into group_member
    for i in range(num_users // 4):
        if i % 10 == 0:
            print(f"User {i}")
        user_id = conn.execute(sqlalchemy.text("""
            SELECT id FROM users ORDER BY random()
            LIMIT 1
        """)).scalar_one()
        new_group = conn.execute(sqlalchemy.text("""
            INSERT INTO groups (name, created_at, owner)
            VALUES (:name, :created_at, :user_id)
            RETURNING groups.id
        """), {"name": f"{fake.word()} {fake.word()}", 
               "created_at": fake.date_time_between(start_date='-1y', end_date='now', tzinfo=None), "user_id" : user_id}).scalar_one()

        conn.execute(sqlalchemy.text("""
            INSERT INTO group_members (group_id, user_id)
            values (:group_id, :user_id)
        """), {"group_id": new_group, "user_id": user_id})
    num_groups = num_users // 4
    # Add users to groups
    for i in range(1, num_groups+1):
        if i % 10 == 0:
            print(f"Group {i}")
        for user in range(3):
            user_id = conn.execute(sqlalchemy.text(
                """
                SELECT id FROM users 
                WHERE id NOT IN (
                    SELECT user_id
                    FROM group_members
                    WHERE group_id = :g_id
                  )
                ORDER BY random()
                LIMIT 1
            """), {"g_id" : i}).scalar_one()
            conn.execute(sqlalchemy.text("""
                INSERT INTO group_members (group_id, user_id)
                values (:group_id, :user_id)
            """), {"group_id": i, "user_id": user_id})

    for group_id in range(1, num_groups+1):
        if group_id % 10 == 0:
            print(f"Trip  {group_id}")
        trip_id = conn.execute(sqlalchemy.text("""
            INSERT INTO shopping_trips (description, payer_id, created_at, group_id)
                SELECT :description, group_members.user_id, :created_at, :group_id 
                FROM group_members
                WHERE group_id = :group_id
                ORDER BY random()
                LIMIT 1
            RETURNING id
        """), {"description": fake.sentence(), "created_at": fake.date_time_between(start_date='-1y', end_date='now', tzinfo=None), "group_id": group_id}).scalar_one()
        trip_id = conn.execute(sqlalchemy.text("""
            INSERT INTO shopping_trips (description, payer_id, created_at, group_id)
                SELECT :description, group_members.user_id, :created_at, :group_id 
                FROM group_members
                WHERE group_id = :group_id
                ORDER BY random()
                LIMIT 1
            RETURNING id
        """), {"description": fake.sentence(), "created_at": fake.date_time_between(start_date='-1y', end_date='now', tzinfo=None), "group_id": group_id}).scalar_one()
    num_trips = num_groups * 2
    for trip_id in range(1,num_trips+1):
        if trip_id % 10 == 0:
            print(f"Item {trip_id}")
        for i in range(np.random.randint(5,12)):
            line_item = conn.execute(sqlalchemy.text("""
                INSERT INTO line_items (item_name, price, quantity, trip_id)
                VALUES (:item_name, :price, :quantity, :trip_id)
                RETURNING id
            """), {"item_name": fake.word(), "price": fake.random_int(min=100, max=40000), "quantity": fake.random_int(min=1, max=10), "trip_id": trip_id}).scalar_one()
            # for j in range(np.random.randint(3,4)):
            conn.execute(sqlalchemy.text("""
                INSERT INTO line_item_members (user_id, line_item_id)
                SELECT group_members.user_id, :line_item_id FROM group_members
                    JOIN shopping_trips ON group_members.group_id = shopping_trips.group_id
                        AND shopping_trips.id = :trip_id
                    LIMIT 3
            """
            ), {"line_item_id": line_item, "trip_id": trip_id})
        transaction_id = conn.execute(sqlalchemy.text("""
            INSERT INTO transactions (description, trip_id, group_id)
            SELECT :desc, :trip_id, group_id
            FROM shopping_trips trips
            WHERE trips.id = :trip_id
            RETURNING id
        """), {"desc": "Paid for trip", "trip_id": trip_id }).scalar_one()

        payer_id = conn.execute(sqlalchemy.text("""
            SELECT payer_id FROM shopping_trips
            WHERE id = :trip_id
        """), {"trip_id": trip_id}).scalar_one()


        conn.execute(sqlalchemy.text("""
            INSERT INTO transaction_ledger (to_id, from_id, change, transaction_id)
                SELECT user_id, :payer_id, :change, :transaction_id
                FROM shopping_trips
                JOIN group_members ON group_members.group_id = shopping_trips.group_id
                WHERE id = :trip_id AND user_id != :payer_id
        """), {"payer_id" : payer_id, "change" : np.random.randint(1000, 150000), "transaction_id" : transaction_id, "trip_id" : trip_id })

    for trip_id in range(1,num_trips+1):
        if trip_id % 10:
            print(f"Transaction {trip_id}")
        for i in range(4):
            transaction_id = conn.execute(sqlalchemy.text("""
                INSERT INTO transactions (description, trip_id, group_id)
                SELECT :desc, :trip_id, group_id
                FROM shopping_trips trips
                WHERE trips.id = :trip_id
                RETURNING id
            """), {"desc": "Paid tripmember", "trip_id": trip_id }).scalar_one()

            payer_id = conn.execute(sqlalchemy.text("""
                SELECT group_members.user_id FROM shopping_trips
                JOIN group_members ON group_members.group_id = shopping_trips.group_id
                WHERE shopping_trips.id = :trip_id AND group_members.user_id != shopping_trips.payer_id
                ORDER BY random()
                LIMIT 1
            """), {"trip_id": trip_id}).scalar_one()

            conn.execute(sqlalchemy.text("""
                INSERT INTO transaction_ledger (to_id, from_id, change, transaction_id)
                    SELECT user_id, :payer_id, :change, :transaction_id
                    FROM shopping_trips
                    JOIN group_members ON group_members.group_id = shopping_trips.group_id
                    WHERE id = :trip_id AND user_id != :payer_id
            """), {"payer_id" : payer_id, "change" : np.random.randint(500, 100000), "transaction_id" : transaction_id, "trip_id" : trip_id })

print("Fake data generation complete.")
