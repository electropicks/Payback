### Workflow 2: Tracking Expenses

**User Story**: Vasanth just got back from a grocery trip with his roommates, where one of his roommates, Suhanth just paid for all of the purchases. He wants to make sure everyone is aware of how much they have to pay Suhanth since they don't all eat the same foods and don't want to pay for groceries they won't be able to make use of. He already has a group set up with all of his roommates so he just needs to start adding the expenses.
- He makes multiple POST requests to `/api/groups/{group_id}/trips/{expense_id}/add` to add all of the items individually. He includes that Suhanth made the purchase for each item, and passes in the names of all roommates that will be paying for each item. 
- He then makes a GET request to `/api/groups/{group_id}/calculate` to see how much each person owes Suhanth.
- After finding out how much he owes, he Venmos Suhanth and makes a POST request to `/api/groups/{group_id}/transactions` to record how much he paid him.

curl -X 'POST' \
  'https://payback-app-rjwr.onrender.com/groups/1/trips/1/add' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "userId": "1",
  "items": [
    {
      "name": "Banana",
      "price": 5,
      "quantity": 1,
      "optedOut": []
    }
  ]
}'

"OK"

curl -X 'POST' \
  'https://payback-app-rjwr.onrender.com/groups/calculate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "userId": "1"
}'

[
  {
    "userId": 2,
    "amount": 33
  },
  {
    "userId": 1,
    "amount": 20
  }
]

curl -X 'POST' \
  'https://payback-app-rjwr.onrender.com/groups/3/transactions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "trip_id": 1,
  "from_id": 1,
  "to_id": 2,
  "amount": 33,
  "description": "Vasanth paid Suhanth (venmo)"
}'

"OK"

### Workflow 3: Correcting an Error
**User Story**: Mark argues with his roommate over the fact that he paid him for lunch yesterday, but his roommate is convinced that he didn't. 
- Mark decides to verify the transactions through the app and makes a GET request to `/api/groups/{group_id}/transactions` to show his roommate.
- His roommate then shows that Mark never actually sent him the payment despite recording it in the app, and mark realizes he forgot to actually pay his roommate. It turns out he also doesn't have enough money to pay him back at the moment, so he decides to remove that transaction for the time being to accurately represent how much he owes his roommate in the app, so he makes a DELETE request to `/api/groups/{group_id}/transactions`

curl -X 'GET' \
  'https://payback-app-rjwr.onrender.com/groups/1/transactions' \
  -H 'accept: application/json'

{
  "transactions": [
    {
      "transaction_id": 1,
      "from_user_id": 1,
      "to_user_id": 2,
      "description": "Paid for trip",
      "date": "2023-11-07T10:05:52.826359+00:00"
    },
    {
      "transaction_id": 2,
      "from_user_id": 1,
      "to_user_id": 1,
      "description": "Paid for trip",
      "date": "2023-11-07T10:05:52.826359+00:00"
    }
  ]
}

curl -X 'POST' \
  'https://payback-app-rjwr.onrender.com/groups/1/trips/1/delete' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "transaction_id": "5"
}'

"OK"