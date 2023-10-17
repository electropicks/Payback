### Workflow 1: Forgot Password

**User Story**: As a user, I forgot my password, so now I need to go through the Forgot Password workflow.

1. User initiates the Forgot Password workflow:

   ```
   POST /forgot-password
   Request Body:
   {
       "email": "user@example.com"
   }
   ```

   The system sends a password reset email to the provided email address.

### Workflow 2: Creating an Account with Google

**User Story**: As a user, I want to easily create an account, so I can just use my Google account.

1. User initiates the Google Sign-Up workflow:

   ```
   GET /auth/google
   ```

   The system redirects the user to Google for authentication.

2. Upon successful Google authentication, the system creates a new account using the Google account details.

### Workflow 3: Creating, Assigning, and Editing Tasks within a Project

1. Creates a new project for the team:

```json
POST /projects
Request Body:
{
    "name": "Project X",
    "description": "A project for Team A",
    "team_id": 1,
    "due_date": "2023-12-31"
}
```

2. Add tasks to the project:

```json
POST /tasks
Request Body:
{
    "project_id": 1,
    "title": "Task 1",
    "description": "Description of Task 1",
    "due_date": "2023-12-31",
    "assigned_to": 2
}
```
3. Edit a task within the project:
  ```json
   PUT /tasks/1
   Request Body:
 {
      "title": "Updated Task Title",
      "description": "Updated task description",
      "due_date": "2024-02-15",
      "assigned_to": 3
 }
  ```
