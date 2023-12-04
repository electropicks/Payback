# Peer Review
## Code Review
### Connor O'Brien
1. Implement error handling and validation, especially for database interactions. Validate data that is being passed to the database.
 - Added data validation where appropriate. See [validation.py](../src/util/validation.py)
2. Include more logging and print statements. Consider using python's logging library.
 - Added logging to endpoints
3. Implement some form of testing (or remove /coverage from .gitignore).
 - Added tests
4. Include more comments or docstrings to explain intent of different sections of the code.
  - Added docstrings to all functions
5. Standardize return strings for POST operations. Some return "OK" while others return different structures. See add_transactions vs. add_line_item.
 - All 'add' methods return the newly created ID now. add_line_items returns "OK" because the user already knows the tripID, and we think it would be better if SQL is used to get all line items associated with the trip when the user needs it.
6. Use a linter to standardize code formatting.
 - Not addressed: code is already Pythonic
7. Finish implementing the signin process.
 - Finished
8. Include more type annotation for inputs, outputs, and local variables.
 - All method signatures have annotated parameters
9. Consider splitting groups.py into multiple .py files to increase clarity between different types of enpoints.
 - Split groups.py into transactions.py & trips.py
10. Include comments/docstring to indicant purpose of different class definitions.
 - Not addressed: Class fields are self-explanatory.
11. Some endpoints (see create_trip for example) will return None if the transaction attempted during the database connection fails. Include error handling or add a return statement outside the 'with' block to fix this.
 - Added httpexceptions outside of the 'with' blocks.
12. Consider using ORM objects for transactions instead of executing raw SQL queries. This would make the more more readable and maintainable.
 - Not addressed: Prof said don't use ORM.
13. Avoid using SQL code for business logic calculations. Use python instead.
 - Not addressed: Can run into concurrency issues if done with python.
### Alfred Madere
1. Improve Response Models
Utilize Pydantic models for response objects to ensure consistency and match the expected schema.
 - Not Addressed: JSON is adequate
2. Improve Error Handling:
Implement error handling to catch exceptions during database operations and return appropriate HTTP status codes and error messages.
 - Added http exceptions outside 'with' blocks
3. Use Dependency Injection for Database Connection:
Employ FastAPI's dependency injection system to manage database connections more effectively, enhancing efficiency and leveraging asynchronous request handling. (we did this in our project so we could easily switch between testing environments)
  - Added testing
4. Ensure Route Naming Consistency
Standardize the naming convention of API routes for intuitiveness and ease of use.
 - Reorganized api for ease of use

5. Use HTTP Status Codes Effectively
Instead of generic responses like "OK," use specific HTTP status codes to convey the result of operations accurately.
 - Return ID for 'add' endpoints, "OK" is appropriate for some endpoints

6. Implement Input Validation in API Endpoints
Enforce validation rules for incoming data to prevent processing and storing invalid data, using Pydantic models for this purpose.
 - Used pydantic models to validate arguments. Also validated id's within SQL

7. Unit and Integration Testing:
Develop a comprehensive suite of unit and integration tests to ensure the application's reliability and handle edge cases effectively. This is maybe the most important one, integration tests prove to you that your api will be functioning as you expect. You don't have much logic to unit test yet.
 - Added tests

8. Implement a Comprehensive Logging Strategy
Create a detailed and structured logging system to provide insights into application behavior and assist in diagnosing issues.
 - Added logging

9. Request Validation Middleware
Use middleware for validating requests before they reach your endpoint logic. This can streamline input validation and provide a central place for request preprocessing.
 - Not addressed: Out of scope for this project

10. Contextual Information in Logs
Include essential context in logs, such as timestamps, endpoint names, and user IDs.
 - Logs print ID. FastAPI/Render already logs endpoint names

11. Rate limiting - eventually
Introduce rate limiting to prevent abuse and ensure fair usage of your API. This can protect your API from excessive traffic and potential denial-of-service attacks.
 - Not Addressed: Eventually

12. Real-time Monitoring and Alerts - eventually
Integrate logging with a monitoring system to provide real-time insights and set up alerts for critical issues.
 - Not Addressed: Eventually


### Sam Bock

1. Use doc strings - this helps developers look over code and see if the function performs as needed. Also to get an idea as to what a program does.
 - Added docstrings
2. Error Handling in OAuth Flow: Implement error handling for potential issues during the OAuth flow. For instance, handle cases where the OAuth response does not contain the expected data. in server.py
 - No longer using OAuth
3. There should be a sign-out function that signs out a user using supabase.auth.signOut(); in users.py
 - No longer using Supabase OAuth
4. For list_group_transactions in groups.py, I would change the for loop to a list comprehension to increase speed and utilize Python's optimized internal mechanism for appending to a list.
 - Switched to list comprehension
5. For create_trip, I feel like the URL would make more sense if you change the URL from /{group_id}/trips to /{group_id}/trips/create. This helps a developer explicitly know that you are dealing with a group_id and trips and that you are creating a new trip. Leaving the URL at `/trips can be vague
 - Split up api into more files
6. For create_or_get_user in users.py, there should be some checks if you create a user and add them to the users table.
 - Added validation of UserId
7. For validation_exception_handler in server.py, I feel like there should be more explicit logs as to what error is happening, rather than just The client sent invalid data!. Try to add specific errors to help track logs as to what functions or database queries are going wrong.
 - We have logging in place that provides specific error messages
8. For delete_transactions, add_transactions, and add_line_item add a description for your return statement instead of "ok" that describes what happened: i.e.: successfully added transaction
 - Return new IDs
9. Add a return statement for failed sql queries. add a return statement outside of the with statement.
 - Raised HTTPExceptions outside of with statements
10. Instead of using res or result for the output of an sql query, change the variable name to a short description as to what the query should be returning for readability.
 - Used more description names instead of res
11. Remove some imports that aren't used. This can help the visibility of code.
 - Unused imports removed
12. Change some class names to help support what purpose they are used for, or add some comment to explain what they should do.
 - Reworked classes
13. OAuth redirect to local host and doesn't return user id or work
 - Fixed

## Schema/API Design
### Connor O'Brien
1. Include updated_at time stamps for all rows/tables to indicate when records were last modified.
 - Ledgerized transactions and auth
2. Use more specific data types where possible. For example, VARCHAR with length limits can be used for fields like name and email to save space and improve data integrity.
 - Not addressed: We don't want to limit name and email length
3. Consider removing the ability to delete transactions. Instead, you could include a deleted_at column within the database. This would improve your ability to recover data and analyze historical trends.
 - Add inverse to transactions ledger instead of deleting records
4. Encrypt fields like 'email' to increase data security.
 - Hashed & salted sensitive fields
5. If you plan on implementing large scale analytics capabilities, consider creating a separate analytics schema that can be used for complex queries without affecting transaction performance.
 - Not addressed: Outside scope of this project
6. Include versioning in the API path to improve transitions to future changes
 - Not addressed: Outside scope of this project
7. Implement rate limiting to prevent abuse of your endpoints
 - Not addressed: Outside scope of this project
8. Include functionality to allow for filtering/sorting in specific GET endpoints.
 - Added search functionality in /groups and /trips
9. Add functionality for large bulk operations. This would reduce the number of API calls.
 - Add_line_items now supports bulk add
10. Include more standardization for structure of return statements from all types of endpoint calls.
  - Return ids for all add endpoints
11. Implement cascading deletes to correctly link together tables and save time/code when deleting or dropping tables.
 - Not addressed: Won't be deleting/dropping tables
12. Avoid using NULL default type for rows. Set a real default type as often as possible.
 - Removed nullable
### Alfred Madere
1. Change name and email in the users table to be non-nullable to ensure every user has this essential information.
 - Made non-nullable
2. Add a unique constraint to the email field in the users table to avoid duplicate email addresses.
 - Added unique constraint
3. Change name in the groups table to be non-nullable to ensure every group has a name.
 - Made non-nullable
4. In the group_members table, remove the identity property from group_id and make group_id and user_id both foreign keys to their respective tables.
 - Fixed key relations
5. Add a unique constraint on (group_id, user_id) in group_members to prevent duplicate memberships.
 - Added unique constraint on the composite key
6. Change description and payer_id in shopping_trips to non-nullable if these fields are always expected.
 - Made non-nullable
7. Make price and quantity non-nullable in trip_line_items and set default values if appropriate.
 - Made non-nullable
8. expense_id in trip_line_items should not be an identity; it should be a foreign key to shopping_trips.
 - Fixed foreign key
9. In trip_item_members, user_id should not have the identity property; it should be a foreign key to users.
 - Fixed foreign key, composite key
10. Make description and expense_id non-nullable in transactions if they are always required.
 - Made non-nullable
11. The transaction_ledger table lacks a primary key. Consider adding a unique identifier as a primary key or using (transaction_id, from_id, to_id) as a composite key.
 - Fixed schema
12. Ensure each field uses the most appropriate data type. For instance, if price in trip_line_items will not have fractional cents, consider using decimal instead of real for more precise financial calculations.
 - Store money as int4
### Sam Bock
1. Only allow NULL values if needed - this should allow for error checking.
 - Made non-nullable
2. Consider using VARCHAR instead of string for name and email to limit the length of data.
 - Not addressed: TEXT is better in Postgres
3. Add a cascading rule for foreign key relationships so deleting a record would delete all other related data on other tables.
 - Not addressed: No records will be deleted
4. Consider adding indexes to help enhance query performance when looking up columns with where clauses.
 - To be done in V5
5. Consider adding constraints where price or value can not be negative. i.e. for prices in trip_line_items
 - Added constraint
6. Use strong hashing algorithms to store emails (salt and hash) or encryption when storing sensitive information like emails.
 - Hashed and salted sensitive fields
7. Add a logs table for server side or client side actions such as user actions (creating groups, purchases) or server actions (404 errors, 500 internal errors, etc.)
 - Added auth ledger. We think our Python logging should be sufficient for other cases
8. Use RESTful design principles and group based on use case i.e. /users, /groups, /transactions, and shopping_trips.
- Now using RESTful design for API, split up API
9. Use standard HTTP codes such as 201 Created for when a new users is created and 404 Not Found when a user doesn't exist.
 - Added appropriate codes
10. Use a rate limiter to prevent abuse of your API. This helps protect your API from being abused by too many requests.
 - Not addressed: Outside of scope
11. Add a soft-delete function with a deleted_at column so you can still access 'deleted' users. This can help restore data if necessary.
 - Added negation row to transactions when a user wants to undo a transactoin
12. Use UUID generator for primary key columns in all tables to help make globally unique ID's. Helps avoid the identity sequence.
 - We feel this is unnecessary at the current scale
13. Add list users in group API
- Added list_users to groups.py