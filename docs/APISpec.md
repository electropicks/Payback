# Payback API Specification

### Base URL
```
https://api.payback.com/v1
```
### Authentication
- API requests require authentication through OAuth2 or API keys.

### Error Handling
- The API returns appropriate HTTP status codes and error messages in JSON format for error handling.


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

#### To log in and obtain a JWT token for authentication - POST /api/auth/login
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
    "token": "your.jwt.token.here"
  }
  ```
### User
#### User profile information - GET /api/users/{user_id}
- Response Body:
  ```json
  {
    "user_id": 1,
    "username": "user123",
    "email": "user123@example.com",
    "other_field": "other_value"
  }
  ```

#### To update user profile information - PUT /api/users/{user_id}
- Request Body:
  ```json
  {
    "email": "new.email@example.com",
    "other_field": "new_value"
  }
  ```
- Response Body:
  ```json
  {
    "message": "User profile updated successfully."
  }
  ```

#### User account deletion successful - DELETE /api/users/{user_id}
- Response Body:
  ```json
  {
    "message": "User account deleted successfully."
  }
  ```
### Group
#### To create a new group - POST /api/groups
- Request Body:
  ```json
  {
    "group_name": "Household Expenses",
    "members": [1, 2, 3]  // User IDs of group members
  }
  ```
- Response Body:
  ```json
  {
    "message": "Group created successfully.",
    "group_id": 123
  }
  ```

#### Group Details - GET /api/groups/{group_id}
- Response Body:
  ```json
  {
    "group_id": 123,
    "group_name": "Household Expenses",
    "members": [1, 2, 3]
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

#### Update group information - PUT /api/groups/{group_id}
- Request Body:
  ```json
  {
    "group_name": "New Group Name"
  }
  ```
- Response Body:
  ```json
  {
    "message": "Group information updated successfully."
  }
  ```

#### Group deletion successful - DELETE /api/groups/{group_id}
- Response Body:
  ```json
  {
    "message": "Group deleted successfully."
  }
  ```
### Expenses
#### List expenses - GET /api/groups/{group_id}/expenses
- Response Body:
  ```json
  {
    "expenses": [
      {
        "expense_id": 1,
        "amount": 50.00,
        "description": "Groceries",
        "date": "2023-10-18"
      },
      {
        "expense_id": 2,
        "amount": 30.00,
        "description": "Dinner",
        "date": "2023-10-17"
      }
    ]
  }
  ```

#### Add expense - POST /api/groups/{group_id}/expenses
- Request Body:
  ```json
  {
    "amount": 25.00,
    "description": "Movie night",
    "date": "2023-10-19"
  }
  ```
- Response Body:
  ```json
  {
    "message": "Expense added successfully.",
    "expense_id": 3
  }
  ```

#### Get details of expense - GET /api/groups/{group_id}/expenses/{expense_id}
- Response Body:
  ```json
  {
    "expense_id": 1,
    "amount": 50.00,
    "description": "Groceries",
    "date": "2023-10-18"
  }
  ```

#### Update Expense - PUT /api/groups/{group_id}/expenses/{expense_id}
- Request Body:
  ```json
  {
    "amount": 55.00,
    "description": "Grocery shopping"
  }
  ```
- Response Body:
  ```json
  {
    "message": "Expense details updated successfully."
  }
  ```

#### Expense deletion - DELETE /api/groups/{group_id}/expenses/{expense_id}
- Response Body:
  ```json
  {
    "message": "Expense deleted successfully."
  }
  ```
### Calculate
#### Calculate Amount Owed GET /api/groups/{group_id}/calculate**
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
### Payment Transactions
#### List Payments - GET /api/groups/{group_id}/transactions
- Response Body:
  ```json
  {
    "transactions": [
      {
        "transaction_id": 1,
        "from_user_id": 1,
        "to_user_id": 2,
        "amount": 10.00,
        "description": "Settling dinner expenses",
        "date": "2023-10-18"
      },
      {
        "transaction_id": 2,
        "from_user_id": 3,
        "to_user_id": 1,
        "amount": 5.00,
        "description": "Repayment for groceries",
        "date": "2023-10-19"
      }
    ]
  }
  ```

#### Record payment transaction - POST /api/groups/{group_id}/transactions
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


#### Delete Payment Transaction - DELETE /api/groups/{group_id}/transactions/{transaction_id}
- Response Body:
  ```json
  {
    "message": "Payment transaction deleted successfully."
  }
  ```
