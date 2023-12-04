import os

import dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker


def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")


engine = create_engine(database_connection_url(), pool_pre_ping=True)

# Reflect the existing database
Base = automap_base()
Base.prepare(engine, reflect=True)

# Create a session-maker
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


print(Base.classes.keys())
# User = Base.classes.users
# Group = Base.classes.groups
# GroupMember = Base.classes.group_members
# ShoppingTrip = Base.classes.shopping_trips
# Transaction = Base.classes.transactions
# TransactionLedger = Base.classes.transaction_ledger
# TripLineItems = Base.classes.line_items
# TripItemMembers = Base.classes.line_item_members
