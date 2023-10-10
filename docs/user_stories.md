## User Stories

As a user, I forgot my password, so now I need to go through the Forgot Password workflow.

As a user, I want to easily create an account, so I can just use my Google account.

As a user, I want to be able to organize multiple related tasks under a Project.

As a user, I realized that two of my projects overlap, so I will merge them into one project.

As a lonely user, I only want to create projects for myself, so I am not required to add other users to a team.

As a group leader, I want to be able to change a task’s deadline if our projections were wrong.

As a group leader, I want to be able to set the priority of tasks for my group, so my group can stay on track to finish the project on time.

As a User, I want to integrate with the Canvas Infrastructure API to retrieve student assignments and add them to my team's projects.

As a group leader, I want to be able to assign tasks to members, so that group members can work on tasks that they will perform best at.

As a user, I want to be able to create, join, view and edit my team, so that I can ensure I am in the right team for my project.

As a user, I have so many projects and tasks that it is hard to find which ones to work on. I want to be able to filter and sort through my tasks.

As a user, I want to be able to delete unwanted tasks, so that I can remove clutter. 

As a user, I want to be able to set which tasks “block” another, to see the dependencies within my tasks and what needs to be completed first.



## Exceptions

Team is missing important fields like Name or Member(s):
When creating a team, validate and check for all required fields. Provide an error message if required fields are not filled out

Due date is in the past:
Do not let users set task due dates prior to current date. Provide an error message if due date is prior to current date.

Task Assignment Conflict:
If two team members attempt to assign the same task to themselves simultaneously, prevent the conflict by informing both users that the task has already been assigned.
Provide options to resolve the conflict, such as reassigning the task or discussing it within the team.

User accidentally removed member from project:
When a user tries to remove a team member from a project, prompt for confirmation to prevent accidental removals.
Display a confirmation dialog to ensure that the user intends to remove the team member from the project.

User accidentally deleted a task:
Present a confirmation dialog asking the user to confirm their intention to delete the task before proceeding.

API Connection Failure:
If there is a problem connecting to the Canvas Infrastructure API to retrieve student assignments, notify users about the issue.
Display a message explaining that the system is experiencing technical difficulties and provide an estimated timeframe for resolution.

User added nonexistent person to team:
Check if user exists before inviting. Prompt user with an error.

User tries to add person to same team twice:
Check whether user is already in team before inviting them, and provide an error if already in the team

User sets the the wrong project name:
Provide option to edit the project and name and ask user to confirm changes. 

User names 2 projects the same thing under the same team:
Ensure project names are unique within a team. Prompt user with error if project with chosen name already exists.

User adds wrong person to team:
Add option to remove someone from team. Ask user to confirm the removal. Only allow the group leader to do so.

Failure to create projects (server side error):
Prompt user with error that their project wasn’t successfully created, and to try again.
