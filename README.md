# TeamFlow API

TeamFlow is a REST API for collaborative team and project management, built with Django and Django REST Framework.

The project focuses on backend architecture, authentication, role-based authorization, relational data modeling, business rules, automated testing, and PostgreSQL integration.

It allows teams to manage members, projects, tasks, comments, dashboards, and notifications through a secure REST API.

---

## Features

### Authentication

- User registration
- JWT authentication
- Access and refresh tokens
- Token verification
- Refresh token rotation
- Refresh token blacklist
- Logout
- Authenticated user profile

### Teams

- Create and retrieve teams
- Team membership management
- Role-based permissions
- Supported roles:
  - Owner
  - Admin
  - Member
- Add and remove members
- Change member roles
- Transfer team ownership
- Prevent multiple owners per team

### Projects

- Create projects inside teams
- List and retrieve projects
- Update and delete projects
- Team-based access control
- Unique project names inside each team

### Tasks

- Create and manage tasks inside projects
- Assign tasks to team members
- Task statuses:
  - Todo
  - In progress
  - Done
- Task priorities:
  - Low
  - Medium
  - High
- Due dates
- Task filtering
- Search by title and description
- Ordering by due date and creation date
- Pagination
- Assigned members can update their own task status
- Owners and admins can fully manage tasks

### Comments

- Add comments to tasks
- List task comments
- Edit comments
- Delete comments
- Comment ownership rules
- Owners and admins can moderate comments
- Pagination

### Dashboard

Team-level dashboard metrics including:

- Total projects
- Total members
- Total tasks
- Tasks by status
- Tasks by priority
- Overdue tasks
- Tasks due soon
- Unassigned tasks
- Per-project task breakdown
- Personal task metrics for the authenticated user

### Notifications

- Private notifications per user
- Read/unread state
- Read timestamp
- Mark notifications as read
- Automatic notification when a task is assigned
- Automatic notification when a task is reassigned
- Prevent unnecessary duplicate notifications
- Users cannot access other users' notifications

---

## Tech Stack

### Backend

- Python 3.13
- Django 6
- Django REST Framework
- Simple JWT
- django-filter

### Database

- PostgreSQL 18
- Django ORM
- Database constraints and indexes

### Dependency Management

- uv
- `pyproject.toml`
- `uv.lock`

### Testing

- pytest
- pytest-django
- Django REST Framework APIClient

The project currently has more than 160 automated tests covering authentication, permissions, team management, projects, tasks, comments, dashboard metrics, and notifications.

---

## Project Structure

```text
teamflow/
│
├── apps/
│   ├── users/
│   ├── teams/
│   ├── projects/
│   ├── tasks/
│   ├── comments/
│   └── notifications/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── manage.py
├── pyproject.toml
├── uv.lock
├── pytest.ini
├── .env.example
└── README.md
```

Each Django application is responsible for a specific business domain, keeping the codebase modular and easier to maintain.

---

## Domain Model

The main relationship between entities is:

```text
User
 │
 ▼
Membership
 │
 ▼
Team
 │
 ▼
Project
 │
 ▼
Task
 ├── Comment
 └── Notification
```

A user belongs to a team through a membership, which also determines the user's role and permissions.

Projects belong to teams, tasks belong to projects, and comments belong to tasks.

---

## Role-Based Permissions

TeamFlow implements authorization rules beyond basic authentication.

### Owner

Can:

- Manage the team
- Add and remove members
- Assign roles
- Transfer ownership
- Create, update, and delete projects
- Create, update, and delete tasks
- Moderate comments

### Admin

Can:

- Manage regular members
- Create, update, and delete projects
- Create, update, and delete tasks
- Moderate comments

Admins cannot transfer ownership or promote users to owner.

### Member

Can:

- View teams they belong to
- View projects
- View tasks
- View and create comments
- Update the status of tasks assigned to them

Members cannot modify administrative team resources.

---

## API Overview

### Authentication

```http
POST /api/auth/register/
POST /api/auth/token/
POST /api/auth/token/refresh/
POST /api/auth/token/verify/
POST /api/auth/logout/
GET  /api/auth/me/
```

### Teams

```http
GET    /api/teams/
POST   /api/teams/
GET    /api/teams/{team_id}/
PATCH  /api/teams/{team_id}/
```

### Team Members

```http
GET    /api/teams/{team_id}/members/
POST   /api/teams/{team_id}/members/
PATCH  /api/teams/{team_id}/members/{user_id}/
DELETE /api/teams/{team_id}/members/{user_id}/

POST   /api/teams/{team_id}/transfer-ownership/
```

### Projects

```http
GET    /api/teams/{team_id}/projects/
POST   /api/teams/{team_id}/projects/
GET    /api/teams/{team_id}/projects/{project_id}/
PATCH  /api/teams/{team_id}/projects/{project_id}/
DELETE /api/teams/{team_id}/projects/{project_id}/
```

### Tasks

```http
GET    /api/teams/{team_id}/projects/{project_id}/tasks/
POST   /api/teams/{team_id}/projects/{project_id}/tasks/

GET    /api/teams/{team_id}/projects/{project_id}/tasks/{task_id}/
PATCH  /api/teams/{team_id}/projects/{project_id}/tasks/{task_id}/
DELETE /api/teams/{team_id}/projects/{project_id}/tasks/{task_id}/
```

Task lists support filtering, searching, ordering, and pagination.

Example:

```http
GET /api/teams/1/projects/2/tasks/?status=todo&priority=high
```

### Comments

```http
GET    /api/teams/{team_id}/projects/{project_id}/tasks/{task_id}/comments/
POST   /api/teams/{team_id}/projects/{project_id}/tasks/{task_id}/comments/

GET    /api/teams/{team_id}/projects/{project_id}/tasks/{task_id}/comments/{comment_id}/
PATCH  /api/teams/{team_id}/projects/{project_id}/tasks/{task_id}/comments/{comment_id}/
DELETE /api/teams/{team_id}/projects/{project_id}/tasks/{task_id}/comments/{comment_id}/
```

### Dashboard

```http
GET /api/teams/{team_id}/dashboard/
```

### Notifications

```http
GET   /api/notifications/
PATCH /api/notifications/{notification_id}/read/
```

---

## Local Setup

### Requirements

You need:

- Python 3.13
- PostgreSQL
- uv
- Git

Clone the repository:

```bash
git clone <repository-url>
cd teamflow
```

Install all dependencies and create the virtual environment:

```bash
uv sync
```

uv will automatically create:

```text
.venv/
```

based on `pyproject.toml` and `uv.lock`.

---

## Environment Variables

Create a `.env` file based on `.env.example`.

Example:

```env
SECRET_KEY=your-local-secret-key
DEBUG=True

DB_NAME=teamflow
DB_USER=teamflow_user
DB_PASSWORD=your-local-database-password
DB_HOST=localhost
DB_PORT=5432
```

Never commit `.env` or real credentials to the repository.

---

## PostgreSQL Setup

Create a PostgreSQL database and application user.

Example:

```sql
CREATE ROLE teamflow_user WITH LOGIN;
```

Set its password securely using PostgreSQL:

```text
\password teamflow_user
```

Create the database:

```sql
CREATE DATABASE teamflow
    OWNER teamflow_user;
```

For local automated testing, the database user also needs permission to create the temporary test database:

```sql
ALTER ROLE teamflow_user CREATEDB;
```

This permission is intended for local development/testing and should not normally be granted to an application database user in production.

---

## Database Migrations

Run:

```bash
uv run python manage.py migrate
```

Check the Django configuration:

```bash
uv run python manage.py check
```

---

## Run the Development Server

```bash
uv run python manage.py runserver
```

The API will be available locally at:

```text
http://127.0.0.1:8000/
```

---

## Running Tests

Run the complete test suite:

```bash
uv run pytest
```

The project currently passes more than 160 automated tests.

Tests cover scenarios such as:

- Authentication
- JWT lifecycle
- Unauthorized access
- Team isolation
- Role permissions
- Membership rules
- Ownership transfer
- Project permissions
- Task assignment
- Filtering and searching
- Pagination
- Comment permissions
- Dashboard metrics
- Notifications

The test suite also runs against PostgreSQL.

---

## Security Considerations

The project includes several security-oriented decisions:

- JWT-based authentication
- Authentication required by default
- Role-based authorization
- Team-based resource isolation
- Users cannot access resources from teams they do not belong to
- Foreign-resource access frequently returns `404` to avoid exposing resource existence
- Passwords are handled through Django authentication
- Database credentials are stored in environment variables
- Secrets are excluded from Git
- Refresh token rotation and blacklist support
- Validation of task assignees against team membership
- Database constraints enforce important business rules

---

## Database Integrity

Important rules are also enforced at database level.

Examples include:

- A user can only belong once to a team
- A team can only have one owner
- Project names are unique inside a team

Indexes are used for commonly queried combinations such as:

- Membership role
- Task status
- Task priority
- Assigned tasks
- Comment creation date
- Notification read state

---

## AI-Assisted Development

AI tools were used during development as a learning and productivity assistant for activities such as:

- Reviewing backend design decisions
- Discussing API architecture
- Exploring testing scenarios
- Debugging errors
- Reviewing security considerations
- Understanding Django and PostgreSQL concepts

Implementation decisions were validated through documentation, manual review, and an automated test suite rather than relying solely on generated code.

---

## Current Status

The backend currently includes:

- Authentication
- Teams and memberships
- Projects
- Tasks
- Comments
- Dashboard
- Notifications
- PostgreSQL integration
- Automated testing

Future improvements may include:

- Background jobs with Celery
- Redis
- Scheduled notifications
- OpenAPI / Swagger documentation
- CI/CD
- Deployment
- Frontend client

---

## Author

**Omar López**

Backend Developer focused on Python, Django, REST APIs, relational databases, and backend architecture.
