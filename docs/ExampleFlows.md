### Workflow 1: Forgot Password

**User Story**: As a user, I forgot my password, so now I need to go through the Forgot Password workflow.
1. User creates a new account with POST /user

2. User forgets password, so they initiate the Forgot Password workflow `POST /user/forgot-password`:

   ```
   POST /forgot-password
   Request Body:
   {
       "email": "user@example.com"
       "hash": as87a8f0f-a
   }
   
   Returns status 200
   ```

   The system sends a password reset email to the provided email address.

### Workflow 2: Creating and updating Teams

**User Story**: As a user, I want to create a new Team with different members.
1. Create new team:
   ```json
   POST /teams
   Request Body:
   {
    "name": "Team A",
    "description": "A team of students working on projects."
   }

   Returns:
   {team_id: integer}
   ```
2. Add member to team:
   ```json
   POST /teams/id/add
   Request Body:
   {
      "user_id": integer
   }
   
   Returns: Status 200
   ```
3. List team members:
   ```json
   GET /teams/id/members
   Returns:
   {
      members: [
         {
            "name",
            "user_id",
            "email"
         }
      ]
   }
   ```

### Workflow 3: Creating, Assigning, and Editing Tasks within a Project
**User Story**: As a user, I want to be able to create, join, view and edit my team, so that I can ensure I am in the right team for my project.
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
POST /tasks/?id={project_id}
Request Body:
{
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
