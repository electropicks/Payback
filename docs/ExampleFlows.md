### Workflow 1: Create New Group

**User Story**: Suhanth wants to create a group for him and his roommates to start tracking their shared expenses. He starts by registering his account:
- Suhanth sends a POST request to /api/auth/register with his registration details, including a username, password, and email.
- After registration, he logs in by sending a POST request to /api/auth/login with his username and password.
- He then makes another POST request to `/api/groups/register` to create the group.
- His roommates can now call POST `/api/groups/{group_id}/join` to join the group and begin tracking their expenses together.
- He also wants to verify that his group was created and that he successfully joined, so he calls POST `/groups/` and sees his group show up.

### Workflow 2: Tracking Expenses

**User Story**: Vasanth just got back from a grocery trip with his roommates, where one of his roommates, Suhanth just paid for all of the purchases. He wants to make sure everyone is aware of how much they have to pay Suhanth since they don't all eat the same foods and don't want to pay for groceries they won't be able to make use of. He already has a group set up with all of his roommates so he just needs to start adding the expenses.
- He makes multiple POST requests to `/api/groups/{group_id}/trips/{trip_id}/add` to add all of the items individually. He includes that Suhanth made the purchase for each item, and passes in the names of all roommates that will be paying for each item. 
- He then makes a GET request to `/api/groups/{group_id}/calculate` to see how much each person owes Suhanth.
- After finding out how much he owes, he Venmos Suhanth and makes a POST request to `/api/groups/{group_id}/transactions` to record how much he paid him.

### Workflow 3: Correcting an Error
**User Story**: Mark argues with his roommate over the fact that he paid him for lunch yesterday, but his roommate is convinced that he didn't. 
- Mark decides to verify the transactions through the app and makes a GET request to `/api/groups/{group_id}/transactions` to show his roommate.
- His roommate then shows that Mark never actually sent him the payment despite recording it in the app, and mark realizes he forgot to actually pay his roommate. It turns out he also doesn't have enough money to pay him back at the moment, so he decides to remove that transaction for the time being to accurately represent how much he owes his roommate in the app, so he makes a DELETE request to `/api/groups/{group_id}/transactions`
