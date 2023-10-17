
## Project Planning API Specification

### Base URL
```
https://api.projectplanner.com/v1
```

### Authentication
- API requests require authentication through OAuth2 or API keys.

### Error Handling
- The API returns appropriate HTTP status codes and error messages in JSON format for error handling.

### Endpoints

#### Teams

##### 1. List Teams
- `GET /teams`
- Get a list of all teams.

##### 2. Create Team
- `POST /teams`
- Create a new team.
- Request Body:
  ```json
  {
    "name": "Team A",
    "description": "A team of students working on projects."
  }
  ```

##### 3. Get Team Details
- `GET /teams/{team_id}`
- Get details of a specific team by ID.

##### 4. Update Team
- `PUT /teams/{team_id}`
- Update team information.
- Request Body:
  ```json
  {
    "name": "New Team Name",
    "description": "Updated team description."
  }
  ```

##### 5. Delete Team
- `DELETE /teams/{team_id}`
- Delete a team and its associated projects.

#### Students

##### 1. List Students
- `GET /students`
- Get a list of all students.

##### 2. Create Student
- `POST /students`
- Create a new student.
- Request Body:
  ```json
  {
    "name": "John Doe",
    "email": "john@example.com",
    "team_id": 1
  }
  ```

##### 3. Get Student Details
- `GET /students/{student_id}`
- Get details of a specific student by ID.

##### 4. Update Student
- `PUT /students/{student_id}`
- Update student information.
- Request Body:
  ```json
  {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "team_id": 2
  }
  ```

##### 5. Delete Student
- `DELETE /students/{student_id}`
- Delete a student and reassign their projects.

#### Projects

##### 1. List Projects
- `GET /projects`
- Get a list of all projects across all teams.

##### 2. Create Project
- `POST /projects`
- Create a new project.
- Request Body:
  ```json
  {
    "name": "Project X",
    "description": "A project for team A",
    "team_id": 1,
    "due_date": "2023-12-31"
  }
  ```

##### 3. Get Project Details
- `GET /projects/{project_id}`
- Get details of a specific project by ID.

##### 4. Update Project
- `PUT /projects/{project_id}`
- Update project information.
- Request Body:
  ```json
  {
    "name": "Updated Project Name",
    "description": "Updated project description",
    "due_date": "2024-02-15"
  }
  ```

##### 5. Delete Project
- `DELETE /projects/{project_id}`
- Delete a project.

#### Tasks

##### 1. List Tasks
- `GET /tasks`
- Get a list of all tasks for a project.

##### 2. Create Task
- `POST /tasks`
- Create a new task for a project.
- Request Body:
  ```json
  {
    "project_id": 1,
    "title": "Task 1",
    "description": "Description of Task 1",
    "due_date": "2023-12-31",
    "assigned_to": 2
  }
  ```

##### 3. Get Task Details
- `GET /tasks/{task_id}`
- Get details of a specific task by ID.

##### 4. Update Task
- `PUT /tasks/{task_id}`
- Update task information.
- Request Body:
  ```json
  {
    "title": "Updated Task Title",
    "description": "Updated task description",
    "due_date": "2024-02-15",
    "assigned_to": 3
  }
  ```

##### 5. Delete Task
- `DELETE /tasks/{task_id}`
- Delete a task.

##### Task Metadata

Tasks may have additional metadata. Metadata can be set using custom fields or attributes, allowing you to customize the information associated with each task according to your specific requirements.

### Pagination
- API responses that return multiple items support pagination via query parameters (e.g., `page` and `per_page`).
