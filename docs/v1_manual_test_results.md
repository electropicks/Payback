# Example Flow
Workflow 1: Create New Group

User Story: Suhanth wants to create a group for him and his roommates to start tracking their shared expenses. He starts by registering his account:

    - Suhanth sends a POST request to /api/auth/register with his registration details, including a username, password, and email.

    - After registration, he logs in by sending a POST request to /api/auth/login with his username and password.

    - He then makes another POST request to /api/groups/register to create the group.

    Curl:
    curl -X 'POST' \
    'http://127.0.0.1:3000/groups/register' \
    -H 'accept: application/json' \
    -H 'access_token: a' \
    -H 'Content-Type: application/json' \
    -d '{
    "userId": "2",
    "name": "Test Group"
    }'

    Response: 
    {
    "group_id": 3
    }

    - His roommates can now call POST /api/groups/{group_id}/join to join the group and begin tracking their expenses together.

    Curl:
    curl -X 'POST' \
        'http://127.0.0.1:3000/groups/3/join?user_id=3' \
        -H 'accept: application/json' \
        -H 'access_token: a' \
        -d ''

    Response:
    {
        "message": "User joined the group successfully."
    }

    - He also wants to verify that his group was created and that he successfully joined, so he calls POST /groups/ and sees his group show up.

    Curl:
    curl -X 'POST' \
        'http://127.0.0.1:3000/groups/' \
        -H 'accept: application/json' \
        -H 'access_token: a' \
        -H 'Content-Type: application/json' \
        -d '{
        "userId": "2"
    }'

    Response:
    [
        {
            "name": "Test Group"
        }
    ]
