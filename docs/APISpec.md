# Payback API Specification
```
https://payback-app-rjwr.onrender.com/
```

## Endpoints
### Auth
#### Register New User - POST /api/auth/register
- Request Body:
  ```json
  {
    "username": "user123",
    "password": "password123",
    "email": "user123@example.com"
  }
  ```
- Response Body:
  ```json
  {
    "message": "User registered successfully."
  }
  ```

#### To log in - POST /api/auth/login
- Request Body:
  ```json
  {
    "username": "user123",
    "password": "password123"
  }
  ```
- Response Body:
  ```json
  {
    "message": "Login successful",
  }
  ```

### Group
#### To create a new group - POST /api/groups/register
- Request Body:
  ```json
  {
    "userId": 0, // Group Owner
    "name": "Groupy Group"
  }
  ```
- Response Body:
  ```json
  {
    "message": "Group created successfully.",
    "group_id": 123
  }
  ```



#### Join a group - POST /api/groups/{group_id}/join
- Request Body:
  ```json
  {
    "user_id": 4  // User ID of the user requesting to join
  }
  ```
- Response Body:
  ```json
  {
    "message": "User joined the group successfully."
  }
  ```

#### Group Transactions - GET /api/groups/{group_id}/transactions
- Response Body:
  ```json
  {
    "transactions": [
      {
        "transaction_id": 199,
        "from_user_id": 121,
        "to_user_id": 115,
        "description": "Paid for trip",
        "date": "2023-12-06T11:18:07.751361+00:00"
      },
      {
        "transaction_id": 200,
        "from_user_id": 121,
        "to_user_id": 120,
        "description": "Paid for trip",
        "date": "2023-12-06T11:18:07.751361+00:00"
      }
  ```

#### Group Trips - GET /api/groups/{group_id}/trips
- Response Body:
  ```json
  {
    "trips": [
      {
        "trip_id": 67,
        "amount": 8921.44,
        "description": "To increase town summer election own discussion stop.",
        "created_at": "2023-07-25T22:58:59.977039+00:00"
      },
      {
        "trip_id": 68,
        "amount": 10839.46,
        "description": "Resource culture general.",
        "created_at": "2022-12-25T10:27:47.236104+00:00"
      }
    ]
  }
  ```

#### Calculate Amount Owed GET /api/groups/{group_id}/calculate
**Complex**
- Response Body:
  ```json
  {
    "balances": {
      "user1": 10.00,
      "user2": -5.00,
      "user3": -5.00
    }
  }
  ```

#### Search Line Items - POST /api/groups/{group_id}/search
**Complex** 
- Request Body:
  ```json
  {
    "query": "search_query"
  }
  ```
- Response Body:
  ```json
  [
    {
      "lineItemId": 1,
      "quantity": 2,
      "price": 10.00,
      "item_name": "Item1",
      "tripId": 123,
      "tripDescription": "Grocery shopping"
    },
    {
      "lineItemId": 2,
      "quantity": 1,
      "price": 5.00,
      "item_name": "Item2",
      "tripId": 124,
      "tripDescription": "Household Supplies"
    }
  ]
  ```

### Trip
#### Get details of expense - GET /api/trips/{trip_id}
- Response Body:
  ```json
  {
    "expense_id": 1,
    "amount": 50.00,
    "description": "Groceries",
    "date": "2023-10-18"
  }
  ```
#### Create trip - POST /api/trips/create
- Request Body:
  ```json
  {
    "userId": 1,
    "groupId": 2,
    "description": "Movie night",
  }
  ```
- Response Body:
  ```json
  {
    "tripId": 3
  }
  ```

#### Get trip items - GET /api/trips/{trip_id}/items
- Response Body:
  ```json
  [
    {
      "Item Name": "Banana",
      "Price": 44.06,
      "Quanity": 8
    }
  ]
  ```

#### Add items - POST /api/trips/{trip_id}/addItems
- Request Body:
  ```json
  {
    "userId": 0,
    "items": [
      {
        "name": "string",
        "price": 0,
        "quantity": 0,
        "optedOut": [
          0
        ]
      }
    ]
  }
  ```
- Response Body:
  ```json
  "OK"
  ```

#### Update Item Price - POST /api/trips/{trip_id}/update_item_price
- Request Body:
  ```json
  {
    "item_id": 4,
    "price": 4.50
  }
  ```
- Response Body:
  ```json
  "OK"
  ```

#### Search Line Items By Trip - POST /api/trips/{trip_id}/search
**Complex**
- Request Body:
  ```json
  {
    "trip_id": 123,
    "query": "search_query"
  }
  ```
- Response Body:
  ```json
  [
    {
      "lineItemId": 1,
      "quantity": 2,
      "price": 10.00,
      "item_name": "Item1",
      "tripDescription": "Grocery shopping"
    },
    {
      "lineItemId": 2,
      "quantity": 1,
      "price": 5.00,
      "item_name": "Item2",
      "tripDescription": "Grocery shopping"
    }
  ]
  ```

### Transaction
#### Record payment transaction - POST /api/transactions/add
- Request Body:
  ```json
  {
    "from_user_id": 1,
    "to_user_id": 2,
    "amount": 10.00,
    "description": "Settling dinner expenses"
  }
  ```

- Response Body:
  ```json
  {
    "message": "Payment transaction recorded successfully."
  }
  ```

#### Delete Payment Transaction - DELETE /api/transactions/{transaction_id}
- Response Body:
  ```json
  {
    "newId": 7
  }
  ```