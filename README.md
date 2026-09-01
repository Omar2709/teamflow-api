**# TeamFlow API**

TeamFlow is a REST API for collaborative team, project, and task management, built with Django and Django REST Framework.

The project focuses on backend architecture, authentication, role-based authorization, relational data modeling, business rules, background processing, automated testing, and PostgreSQL integration.

It allows teams to manage members, projects, tasks, comments, dashboards, and notifications through a secure REST API, while using PostgreSQL for relational persistence and Celery with Redis for background processing.

**---**

**## Features**

**### Authentication**

\- User registration

\- JWT authentication

\- Access and refresh tokens

\- Token verification

\- Refresh token rotation

\- Refresh token blacklist

\- Logout

\- Authenticated user profile

**### Teams**

\- Create and retrieve teams

\- Team membership management

\- Role-based permissions

\- Supported roles:

  - Owner

  - Admin

  - Member

\- Add and remove members

\- Change member roles

\- Transfer team ownership

\- Prevent multiple owners per team

\- Isolate resources between teams

**### Projects**

\- Create projects inside teams

\- List and retrieve projects

\- Update and delete projects

\- Team-based access control

\- Unique project names inside each team

**### Tasks**

\- Create and manage tasks inside projects

\- Assign tasks to team members

\- Reassign tasks

\- Task statuses:

  - Todo

  - In progress

  - Done

\- Task priorities:

  - Low

  - Medium

  - High

\- Optional due dates

\- Task filtering

\- Search by title and description

\- Ordering by due date and creation date

\- Pagination

\- Assigned members can update their own task status

\- Owners and admins can fully manage tasks

\- Task assignees must belong to the corresponding team

**### Comments**

\- Add comments to tasks

\- List task comments

\- Edit comments

\- Delete comments

\- Comment ownership rules

\- Owners and admins can moderate comments

\- Pagination

\- Team-based access isolation

**### Dashboard**

Team-level dashboard metrics including:

\- Total members

\- Total projects

\- Total tasks

\- Tasks by status

\- Tasks by priority

\- Overdue tasks

\- Tasks due soon

\- Unassigned tasks

\- Per-project task breakdown

\- Personal task metrics for the authenticated user

\- Personal overdue task metrics

\- Personal due-soon task metrics

**### Notifications**

\- Private notifications per user

\- Read/unread state

\- Read timestamp

\- Mark notifications as read

\- Automatic notification when a task is assigned

\- Automatic notification when a task is reassigned

\- Automatic notification when someone comments on a task

\- Notifications for tasks approaching their due date

\- Duplicate notification prevention

\- Users cannot access other users' notifications

\- Due-soon notification logic implemented as an idempotent service

\- Celery task integration for background execution

**---**

**## Tech Stack**

**### Backend**

\- Python 3.13

\- Django 6

\- Django REST Framework

\- Simple JWT

\- django-filter

\- Celery 5.6

**### Database**

\- PostgreSQL 18

\- Django ORM

\- Database constraints

\- Database indexes

**### Background Processing**

\- Celery

\- Redis 8

\- Redis as Celery message broker

\- Docker Compose for local Redis infrastructure

**### Dependency Management**

\- uv

\- \`pyproject.toml\`

\- \`uv.lock\`

**### Testing**

\- pytest

\- pytest-django

\- Django REST Framework APIClient

\- PostgreSQL test database

**### Infrastructure and Tools**

\- Docker

\- Docker Compose

\- Git

\- GitHub

\- GitHub Actions — Continuous Integration

\- WSL 2 / Linux containers when running Docker Desktop on Windows

The project currently contains **\*\*201 passing automated tests\*\*** covering authentication, authorization, teams, projects, tasks, comments, dashboards, notifications, database behavior, and Celery integration.

**---**

**## Continuous Integration**

TeamFlow includes a GitHub Actions CI pipeline that runs automatically on pushes and pull requests targeting `main`.

The pipeline uses PostgreSQL 18.6 and validates:

\- Dependency reproducibility with `uv.lock`

\- Django system checks

\- Pending model migrations

\- OpenAPI schema generation and validation

\- The complete automated test suite

Current test suite:

\- 201 automated tests

\- Unit and integration tests

\- Authentication and authorization tests

\- API behavior tests

\- Celery notification tests

\- OpenAPI regression tests

\- ORM query regression tests for N+1 detection

**---**

**## Project Structure**

\`\`\`text

teamflow/

│

├── apps/

│   ├── users/

│   │   ├── models.py

│   │   ├── serializers.py

│   │   ├── views.py

│   │   ├── urls.py

│   │   └── tests.py

│   │

│   ├── teams/

│   │   ├── models.py

│   │   ├── dashboard.py

│   │   ├── permissions.py

│   │   ├── serializers.py

│   │   ├── views.py

│   │   ├── urls.py

│   │   └── tests.py

│   │

│   ├── projects/

│   │   ├── models.py

│   │   ├── permissions.py

│   │   ├── serializers.py

│   │   ├── views.py

│   │   ├── urls.py

│   │   └── tests.py

│   │

│   ├── tasks/

│   │   ├── models.py

│   │   ├── pagination.py

│   │   ├── permissions.py

│   │   ├── serializers.py

│   │   ├── views.py

│   │   ├── urls.py

│   │   └── tests.py

│   │

│   ├── comments/

│   │   ├── models.py

│   │   ├── pagination.py

│   │   ├── permissions.py

│   │   ├── serializers.py

│   │   ├── views.py

│   │   ├── urls.py

│   │   └── tests.py

│   │

│   └── notifications/

│       ├── models.py

│       ├── serializers.py

│       ├── services.py

│       ├── tasks.py

│       ├── views.py

│       ├── urls.py

│       └── tests.py

│

├── config/

│   ├── celery.py

│   ├── settings.py

│   ├── urls.py

│   └── ...

│

├── compose.yaml

├── manage.py

├── pyproject.toml

├── uv.lock

├── pytest.ini

├── .env.example

└── README.md

\`\`\`

Each Django application is responsible for a specific business domain, helping keep the codebase modular and maintainable.

Business logic that does not belong directly to HTTP views is separated into service functions. Celery tasks reuse those services instead of duplicating business rules.

**---**

**## Domain Model**

The main relationships between entities can be represented as:

\`\`\`text

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

\`\`\`

A user belongs to a team through a \`Membership\`, which also determines the user's role and permissions.

Projects belong to teams, tasks belong to projects, and comments belong to tasks.

Notifications belong to users and may optionally reference a task.

**---**

**## Role-Based Authorization**

TeamFlow implements authorization rules beyond basic authentication.

**### Owner**

Can:

\- Manage the team

\- Add and remove members

\- Assign roles

\- Transfer team ownership

\- Create, update, and delete projects

\- Create, update, and delete tasks

\- Moderate comments

A team can only have one owner.

**### Admin**

Can:

\- Manage regular members

\- Create, update, and delete projects

\- Create, update, and delete tasks

\- Moderate comments

Admins cannot transfer ownership or assign the owner role.

**### Member**

Can:

\- View teams they belong to

\- View projects

\- View tasks

\- View and create comments

\- Edit their own comments

\- Delete their own comments

\- Update the status of tasks assigned to them

Members cannot modify administrative team resources.

**---**

**## API Overview**

**### Authentication**

\`\`\`http

POST /api/auth/register/

POST /api/auth/token/

POST /api/auth/token/refresh/

POST /api/auth/token/verify/

POST /api/auth/logout/

GET  /api/auth/me/

\`\`\`

**### Teams**

\`\`\`http

GET   /api/teams/

POST  /api/teams/

GET   /api/teams/{team\_id}/

PATCH /api/teams/{team\_id}/

\`\`\`

**### Team Members**

\`\`\`http

GET    /api/teams/{team\_id}/members/

POST   /api/teams/{team\_id}/members/

PATCH  /api/teams/{team\_id}/members/{user\_id}/

DELETE /api/teams/{team\_id}/members/{user\_id}/

POST   /api/teams/{team\_id}/transfer-ownership/

\`\`\`

**### Projects**

\`\`\`http

GET    /api/teams/{team\_id}/projects/

POST   /api/teams/{team\_id}/projects/

GET    /api/teams/{team\_id}/projects/{project\_id}/

PATCH  /api/teams/{team\_id}/projects/{project\_id}/

DELETE /api/teams/{team\_id}/projects/{project\_id}/

\`\`\`

**### Tasks**

\`\`\`http

GET  /api/teams/{team\_id}/projects/{project\_id}/tasks/

POST /api/teams/{team\_id}/projects/{project\_id}/tasks/

GET    /api/teams/{team\_id}/projects/{project\_id}/tasks/{task\_id}/

PATCH  /api/teams/{team\_id}/projects/{project\_id}/tasks/{task\_id}/

DELETE /api/teams/{team\_id}/projects/{project\_id}/tasks/{task\_id}/

\`\`\`

Task lists support filtering, searching, ordering, and pagination.

Example:

\`\`\`http

GET /api/teams/1/projects/2/tasks/?status=todo&priority=high

\`\`\`

Search example:

\`\`\`http

GET /api/teams/1/projects/2/tasks/?search=authentication

\`\`\`

Ordering example:

\`\`\`http

GET /api/teams/1/projects/2/tasks/?ordering=due\_date

\`\`\`

**### Comments**

\`\`\`http

GET  /api/teams/{team\_id}/projects/{project\_id}/tasks/{task\_id}/comments/

POST /api/teams/{team\_id}/projects/{project\_id}/tasks/{task\_id}/comments/

GET    /api/teams/{team\_id}/projects/{project\_id}/tasks/{task\_id}/comments/{comment\_id}/

PATCH  /api/teams/{team\_id}/projects/{project\_id}/tasks/{task\_id}/comments/{comment\_id}/

DELETE /api/teams/{team\_id}/projects/{project\_id}/tasks/{task\_id}/comments/{comment\_id}/

\`\`\`

**### Dashboard**

\`\`\`http

GET /api/teams/{team\_id}/dashboard/

\`\`\`

The dashboard provides aggregated team and personal task metrics.

**### Notifications**

\`\`\`http

GET   /api/notifications/

PATCH /api/notifications/{notification\_id}/read/

\`\`\`

Users only have access to their own notifications.

**---**

**## Background Processing Architecture**

TeamFlow separates business rules from the mechanism used to execute them.

For example, notifications for tasks approaching their due date are implemented through a reusable service.

\`\`\`text

Celery Task

    │

    ▼

Notification Service

    │

    ▼

Django ORM

    │

    ▼

PostgreSQL

\`\`\`

Redis acts as the message broker for Celery:

\`\`\`text

Application

    │

    │ task message

    ▼

Redis

    │

    ▼

Celery Worker

    │

    ▼

Notification Service

    │

    ▼

PostgreSQL

\`\`\`

The due-soon notification service is idempotent, preventing repeated executions from generating duplicate notifications for the same user and task.

The business rules can therefore be tested synchronously without requiring Redis or a running Celery worker.

Celery is responsible for background execution, while the service layer remains responsible for the actual business logic.

**---**

**## Notification Rules**

**### Task Assignment**

When a task is assigned or reassigned:

\`\`\`text

Task assigned

      ↓

new assignee

      ↓

TASK\_ASSIGNED notification

\`\`\`

No notification is created when:

\- The task remains assigned to the same user

\- The task has no assignee

\- A user assigns the task to themselves

**### Comments**

When someone comments on a task, notifications may be sent to:

\- The task creator

\- The current task assignee

The system avoids:

\- Notifying the comment author about their own comment

\- Sending duplicate notifications when the creator and assignee are the same user

**### Due-Soon Tasks**

A task is considered due soon when:

\`\`\`text

due\_date > today

AND

due\_date <= today + 7 days

AND

status != done

AND

assigned\_to != null

\`\`\`

Repeated execution does not create duplicate due-soon notifications.

**---**

**## Local Setup**

**### Requirements**

You need:

\- Python 3.13

\- PostgreSQL

\- uv

\- Git

\- Docker Desktop

\- Docker Compose

On Windows, Docker Desktop can use WSL 2 as its Linux container backend.

**---**

**## Clone the Repository**

\`\`\`bash

git clone \<repository-url>

cd teamflow

\`\`\`

Replace \`\<repository-url>\` with the actual repository URL.

**---**

**## Install Dependencies**

TeamFlow uses \`uv\` for dependency and virtual environment management.

Run:

\`\`\`bash

uv sync

\`\`\`

uv will create the project's virtual environment automatically:

\`\`\`text

.venv/

\`\`\`

based on:

\`\`\`text

pyproject.toml

uv.lock

\`\`\`

You do not need to manually create a virtual environment or use \`pip install -r requirements.txt\`.

**---**

**## Environment Variables**

Create a \`.env\` file based on \`.env.example\`.

Example:

\`\`\`env

SECRET\_KEY=your-local-secret-key

DEBUG=True

DB\_NAME=teamflow

DB\_USER=teamflow\_user

DB\_PASSWORD=your-local-database-password

DB\_HOST=localhost

DB\_PORT=5432

CELERY\_BROKER\_URL=redis\://localhost:6379/0

\`\`\`

Never commit \`.env\` or real credentials to the repository.

**---**

**## PostgreSQL Setup**

Create a PostgreSQL application user:

\`\`\`sql

CREATE ROLE teamflow\_user WITH LOGIN;

\`\`\`

Set its password securely from PostgreSQL:

\`\`\`text

\password teamflow\_user

\`\`\`

Create the database:

\`\`\`sql

CREATE DATABASE teamflow

    OWNER teamflow\_user;

\`\`\`

For local automated testing, the database user also needs permission to create the temporary test database:

\`\`\`sql

ALTER ROLE teamflow\_user CREATEDB;

\`\`\`

The \`CREATEDB\` permission is useful for local testing because pytest/Django creates a temporary database such as:

\`\`\`text

test\_teamflow

\`\`\`

This permission should not normally be granted to the application's database user in production.

**---**

**## Database Migrations**

Run:

\`\`\`bash

uv run python manage.py migrate

\`\`\`

Check the Django configuration:

\`\`\`bash

uv run python manage.py check

\`\`\`

Expected result:

\`\`\`text

System check identified no issues

\`\`\`

**---**

**## Redis**

Redis is used as the Celery message broker and runs locally through Docker Compose.

Start Redis:

\`\`\`bash

docker compose up -d redis

\`\`\`

Check its status:

\`\`\`bash

docker compose ps

\`\`\`

Test Redis:

\`\`\`bash

docker compose exec redis redis-cli ping

\`\`\`

Expected response:

\`\`\`text

PONG

\`\`\`

Redis is mapped locally to:

\`\`\`text

127.0.0.1:6379

\`\`\`

rather than being unnecessarily exposed to the entire local network.

Stop the local infrastructure with:

\`\`\`bash

docker compose down

\`\`\`

**---**

**## Celery**

Celery is integrated with Django through:

\`\`\`text

config/celery.py

\`\`\`

Celery automatically discovers tasks defined inside Django applications.

The notifications application currently defines:

\`\`\`text

notifications.notify\_due\_soon\_tasks

\`\`\`

The task delegates business logic to:

\`\`\`text

apps/notifications/services.py

\`\`\`

instead of duplicating notification rules inside the Celery task itself.

This separation makes the code easier to maintain and test.

At the current stage of the project, Celery configuration and task behavior are implemented and covered by automated tests.

Containerized Celery workers and periodic scheduling with Celery Beat are planned as the next infrastructure improvements.

**---**

**## Run the Development Server**

Start Redis first if working with Celery-related functionality:

\`\`\`bash

docker compose up -d redis

\`\`\`

Then start Django:

\`\`\`bash

uv run python manage.py runserver

\`\`\`

The API will be available locally at:

\`\`\`text

http\://127.0.0.1:8000/

\`\`\`

**---**

**## Running Tests**

Run the complete test suite:

\`\`\`bash

uv run pytest

\`\`\`

The project currently contains:

\`\`\`text

201 passing tests

\`\`\`

The suite covers scenarios such as:

\- User registration

\- JWT authentication

\- Access token handling

\- Refresh token rotation

\- Token blacklist

\- Logout

\- Unauthorized access

\- Team isolation

\- Role-based permissions

\- Membership rules

\- Team ownership transfer

\- Project permissions

\- Project uniqueness constraints

\- Task creation

\- Task assignment

\- Task reassignment

\- Task permissions

\- Task status updates

\- Filtering

\- Searching

\- Ordering

\- Pagination

\- Comment creation

\- Comment ownership

\- Comment moderation

\- Dashboard metrics

\- Overdue task calculations

\- Due-soon task calculations

\- User notifications

\- Task assignment notifications

\- Comment notifications

\- Due-soon notifications

\- Notification idempotency

\- Celery configuration

\- Celery task registration

\- Celery task behavior

\- OpenAPI schema regression tests

\- ORM query regression tests for N+1 detection

The test suite runs against PostgreSQL.

Celery service behavior is tested synchronously so the normal unit/integration test suite does not depend on a running Redis container or Celery worker.

**---**

**## Database Integrity**

Important business rules are also enforced at database level.

Examples include:

\- A user can only belong once to a team

\- A team can only have one owner

\- Project names are unique inside each team

Database indexes are used for commonly queried combinations such as:

\- Membership team and role

\- Membership user and role

\- Task project and status

\- Task project and priority

\- Task assignee and status

\- Comment task and creation date

\- Notification user and read state

\- Notification user and creation date

This helps move important integrity rules closer to the database instead of relying exclusively on application code.

**---**

**## Database Performance**

Critical read endpoints include regression tests that verify the number of SQL queries does not grow linearly with the number of returned objects.

The audit currently covers:

\- Teams

\- Projects

\- Tasks

\- Comments

\- Notifications

\- Team dashboard

During the audit, an N+1 query issue was identified in the team list serialization and optimized from:

\- 1 team: 2 queries

\- 10 teams: 11 queries

to:

\- 1 team: 1 query

\- 10 teams: 1 query

The dashboard also remains constant at 5 queries when growing from an empty workload to 10 projects and 100 tasks.

**---**

**## Security Considerations**

The project includes several security-oriented decisions:

\- JWT-based authentication

\- Authentication required by default

\- Role-based authorization

\- Team-based resource isolation

\- Users cannot access resources from teams they do not belong to

\- Foreign-resource access frequently returns \`404\` to avoid exposing resource existence

\- Passwords are managed through Django's authentication system

\- Database credentials are stored in environment variables

\- Application secrets are excluded from Git

\- Refresh token rotation

\- Refresh token blacklist

\- Validation of task assignees against team membership

\- Database constraints enforce important business rules

\- Redis is bound to localhost in the local development configuration

\- Users cannot access or modify another user's notifications

**---**

**## Dependency Management with uv**

TeamFlow uses \`uv\` instead of \`pip + requirements.txt\`.

The main dependency files are:

\`\`\`text

pyproject.toml

uv.lock

\`\`\`

**### Install or synchronize dependencies**

\`\`\`bash

uv sync

\`\`\`

**### Add a production dependency**

\`\`\`bash

uv add package-name

\`\`\`

**### Add a development dependency**

\`\`\`bash

uv add --dev package-name

\`\`\`

**### Remove a dependency**

\`\`\`bash

uv remove package-name

\`\`\`

**### View the dependency tree**

\`\`\`bash

uv tree

\`\`\`

**### Run Python**

\`\`\`bash

uv run python

\`\`\`

**### Run Django commands**

\`\`\`bash

uv run python manage.py \<command>

\`\`\`

**### Run tests**

\`\`\`bash

uv run pytest

\`\`\`

\`uv.lock\` is committed to Git so the project can reproduce a consistent dependency graph across development environments and CI/CD.

**---**

**## Development Workflow**

A typical local workflow is:

\`\`\`bash

docker compose up -d redis

uv sync

uv run python manage.py migrate

uv run python manage.py check

uv run pytest

uv run python manage.py runserver

\`\`\`

**---**

**## AI-Assisted Development**

AI tools were used during development as a learning and engineering assistant for activities such as:

\- Reviewing backend architecture decisions

\- Discussing API and authorization design

\- Exploring edge cases

\- Designing testing scenarios

\- Debugging implementation errors

\- Debugging development environment issues

\- Reviewing security considerations

\- Understanding Django and Django REST Framework concepts

\- Understanding PostgreSQL behavior

\- Reviewing Docker and Redis integration

\- Understanding Celery and background processing

\- Comparing implementation alternatives

AI-generated suggestions were not incorporated blindly.

Proposed solutions were reviewed, adapted to the project's architecture, verified against expected behavior, and validated through automated tests.

The project currently contains **\*\*201 passing automated tests\*\*** covering business rules, permissions, database behavior, API endpoints, dashboards, notifications, and Celery integration.

**---**

**## Current Status**

The backend currently includes:

\- JWT authentication

\- Custom user model

\- Teams

\- Role-based memberships

\- Ownership transfer

\- Projects

\- Tasks

\- Task filters

\- Task search

\- Task ordering

\- Task pagination

\- Comments

\- Comment moderation

\- Comment pagination

\- Team dashboard

\- Personal dashboard metrics

\- User notifications

\- Automatic task assignment notifications

\- Automatic comment notifications

\- Due-soon notification processing

\- Celery integration

\- Redis broker infrastructure

\- PostgreSQL integration

\- Docker Compose for local Redis infrastructure

\- uv dependency management

\- GitHub Actions continuous integration

\- OpenAPI schema validation and regression coverage

\- ORM query regression tests for N+1 detection

\- **\*\*201 automated tests\*\***

**---**

**## Planned Improvements**

Future improvements include:

\- Containerized Celery worker

\- Celery Beat for scheduled background jobs

\- End-to-end asynchronous task execution

\- OpenAPI / Swagger documentation

\- API documentation improvements

\- Continuous deployment pipeline

\- Production deployment

\- Production-ready environment configuration

\- Additional observability and logging

\- Frontend client

**---**

**## Engineering Goals**

TeamFlow is intended to demonstrate more than basic CRUD operations.

The project focuses on:

\- REST API design

\- Relational database modeling

\- Authentication

\- Authorization

\- Business rules

\- Data isolation

\- Database integrity

\- Service-layer design

\- Background processing

\- Idempotency

\- Testing

\- Security

\- Maintainability

\- Reproducible development environments

**---**

**## Author**

**\*\*Omar López\*\***

Backend Developer focused on Python, Django, REST APIs, PostgreSQL, backend architecture, automated testing, and asynchronous processing.