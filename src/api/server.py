import json
import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.api import auth, groups, transactions, trips

description = """
Get what you are owed.
"""

app = FastAPI(
    title="payBack",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "suhanth alluri",
        "email": "alluri@calpoly.edu",
    },
)

app.include_router(groups.router)
app.include_router(transactions.router)
app.include_router(trips.router)
app.include_router(auth.router)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"The client sent invalid data!: {exc}")
    exc_json = json.loads(exc.json())
    response = {"message": [], "data": None}
    for error in exc_json:
        response['message'].append(f"{error['loc']}: {error['msg']}")

    return JSONResponse(response, status_code=422)


@app.get("/")
async def root():
    return {"message": "Get PAYBACK"}
