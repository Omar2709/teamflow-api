# TeamFlow API

TeamFlow is a REST API for collaborative team, project, and task management, built with Django and Django REST Framework.

The project focuses on backend architecture, authentication, role-based authorization, relational data modeling, business rules, background processing, automated testing, database performance, continuous integration, and production-oriented configuration.

It allows teams to manage members, projects, tasks, comments, dashboards, and notifications through a secure REST API, while using PostgreSQL for relational persistence, Redis as a message broker, and Celery for asynchronous background processing.

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
- Isolate resources between teams

### Projects

- Create projects inside teams
- List and retrieve projects
- Update and delete projects
- Team-based access control
- Unique project names inside each team

### Tasks

- Create and manage tasks inside projects
- Assign tasks to team members
- Reassign tasks
- Task statuses:
  - Todo
  - In progress
  - Done
- Task priorities:
  - Low
  - Medium
  - High
- Optional due dates
- Task filtering
- Search by title and description
- Ordering by due date and creation date
- Pagination
- Assigned members can update their own task status
- Owners and admins can fully manage tasks
- Task assignees must belong to the corresponding team

### Comments

- Add comments to tasks
- List task comments
- Edit comments
- Delete comments
- Comment ownership rules
- Owners and admins can moderate comments
- Pagination
- Team-based access isolation

### Dashboard

Team-level dashboard metrics including:

- Total members
- Total projects
- Total tasks
- Tasks by status
- Tasks by priority
- Overdue tasks
- Tasks due soon
- Unassigned tasks
- Per-project task breakdown
- Personal task metrics for the authenticated user
- Personal overdue task metrics
- Personal due-soon task metrics

### Notifications

- Private notifications per user
- Read/unread state
- Read timestamp
- Mark notifications as read
- Automatic notification when a task is assigned
- Automatic notification when a task is reassigned
- Automatic notification when someone comments on a task
- Notifications for tasks approaching their due date
- Duplicate notification prevention
- Users cannot access other users' notifications
- Due-soon notification logic implemented as an idempotent service
- Celery task integration for background execution
- Periodic due-soon notification execution with Celery Beat

---

## Tech Stack

### Backend

- Python 3.13
- Django 6
- Django REST Framework
- Simple JWT
- django-filter
- drf-spectacular
- Gunicorn
- Celery 5.6

### Database

- PostgreSQL 18
- Django ORM
- Database constraints
- Database indexes
- Query annotations and aggregations

### Background Processing

- Celery
- Celery Beat
- Redis 8
- Redis as Celery message broker
- Containerized Celery worker
- Containerized Celery Beat scheduler

### Dependency Management

- uv
- `pyproject.toml`
- `uv.lock`

### Testing

- pytest
- pytest-django
- django-stubs
- djangorestframework-stubs
- Django REST Framework APIClient
- PostgreSQL test database
- OpenAPI regression tests
- ORM query regression tests

### Infrastructure and Tools

- Docker
- Docker Compose
- Gunicorn
- Git
- GitHub
- GitHub Actions
- PostgreSQL service containers in CI
- WSL 2 / Linux containers when running Docker Desktop on Windows

The project currently contains **201 passing automated tests** covering authentication, authorization, teams, projects, tasks, comments, dashboards, notifications, database behavior, Celery integration, OpenAPI contracts, and ORM query performance.

---

## Architecture

A simplified view of the current architecture is:

```text
Client
  │
  ▼
Gunicorn
  │
  ▼
Django REST Framework
  │
  ├──────────────► PostgreSQL
  │
  ▼
Redis
  │
  ├──────────────► Celery Worker
  │                   │
  │                   ▼
  │             Notification Services
  │                   │
  │                   ▼
  │               PostgreSQL
  │
  └──────────────► Celery Beat
                      │
                      ▼
                Scheduled Tasks
```

Docker Compose is used locally to run:

```text
web
redis
celery-worker
celery-beat
```

The `web` service executes Django through Gunicorn instead of Django's development server.

---

## Continuous Integration

TeamFlow includes a GitHub Actions CI pipeline that runs automatically on pushes and pull requests targeting `main`.

The pipeline uses PostgreSQL 18.6 and validates:

- Dependency reproducibility with `uv.lock`
- Django system checks
- Pending model migrations
- OpenAPI schema generation and validation
- The complete automated test suite

The current CI pipeline performs:

```text
Checkout repository
        ↓
Set up uv and Python
        ↓
Install dependencies
        ↓
Start PostgreSQL service
        ↓
Django system check
        ↓
Migration consistency check
        ↓
OpenAPI validation
        ↓
pytest
```

Current test suite:

- 201 automated tests
- Unit and integration tests
- Authentication and authorization tests
- API behavior tests
- Celery notification tests
- OpenAPI regression tests
- ORM query regression tests for N+1 detection

The CI environment uses ephemeral credentials and does not require local `.env` secrets.

---

## Project Structure

```text
teamflow/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── apps/
│   ├── users/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   │
│   ├── teams/
│   │   ├── models.py
│   │   ├── dashboard.py
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   │
│   ├── projects/
│   │   ├── models.py
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   │
│   ├── tasks/
│   │   ├── models.py
│   │   ├── pagination.py
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   │
│   ├── comments/
│   │   ├── models.py
│   │   ├── pagination.py
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   │
│   └── notifications/
│       ├── models.py
│       ├── serializers.py
│       ├── services.py
│       ├── tasks.py
│       ├── views.py
│       ├── urls.py
│       └── tests.py
│
├── config/
│   ├── celery.py
│   ├── settings.py
│   ├── settings_test.py
│   ├── urls.py
│   ├── wsgi.py
│   └── ...
│
├── Dockerfile
├── compose.yaml
├── manage.py
├── pyproject.toml
├── uv.lock
├── pytest.ini
├── .env.example
└── README.md
```

Each Django application is responsible for a specific business domain, helping keep the codebase modular and maintainable.

Business logic that does not belong directly to HTTP views is separated into service functions. Celery tasks reuse those services instead of duplicating business rules.

---

## Domain Model

The main relationships between entities can be represented as:

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

A user belongs to a team through a `Membership`, which also determines the user's role and permissions.

Projects belong to teams, tasks belong to projects, and comments belong to tasks.

Notifications belong to users and may optionally reference a task.

---

## Role-Based Authorization

TeamFlow implements authorization rules beyond basic authentication.

### Owner

Can:

- Manage the team
- Add and remove members
- Assign roles
- Transfer team ownership
- Create, update, and delete projects
- Create, update, and delete tasks
- Moderate comments

A team can only have one owner.

### Admin

Can:

- Manage regular members
- Create, update, and delete projects
- Create, update, and delete tasks
- Moderate comments

Admins cannot transfer ownership or assign the owner role.

### Member

Can:

- View teams they belong to
- View projects
- View tasks
- View and create comments
- Edit their own comments
- Delete their own comments
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
GET   /api/teams/
POST  /api/teams/
GET   /api/teams/{team_id}/
PATCH /api/teams/{team_id}/
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

Filter example:

```http
GET /api/teams/1/projects/2/tasks/?status=todo&priority=high
```

Search example:

```http
GET /api/teams/1/projects/2/tasks/?search=authentication
```

Ordering example:

```http
GET /api/teams/1/projects/2/tasks/?ordering=due_date
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

The dashboard provides aggregated team and personal task metrics.

### Notifications

```http
GET   /api/notifications/
PATCH /api/notifications/{notification_id}/read/
```

Users only have access to their own notifications.

---

## OpenAPI Documentation

TeamFlow exposes an OpenAPI 3 schema using `drf-spectacular`.

Available endpoints:

```text
/api/schema/   → OpenAPI schema
/api/docs/     → Swagger UI
/api/redoc/    → ReDoc
```

Swagger includes support for JWT authentication and documents protected endpoints using a Bearer authentication scheme.

Custom response schemas are defined for endpoints that cannot be fully inferred automatically, including:

- Authenticated user profile
- Logout request and responses
- Team dashboard

The project also contains regression tests to ensure important OpenAPI contracts remain available and correctly typed.

Schema validation can be executed with:

```bash
uv run python manage.py spectacular --validate
```

The current schema validates without OpenAPI generation errors or warnings.

---

## Background Processing Architecture

TeamFlow separates business rules from the mechanism used to execute them.

For example, notifications for tasks approaching their due date are implemented through a reusable service.

```text
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
```

Redis acts as the message broker for Celery:

```text
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
```

Scheduled execution uses Celery Beat:

```text
Celery Beat
    │
    │ periodic task
    ▼
Redis
    │
    ▼
Celery Worker
    │
    ▼
notifications.notify_due_soon_tasks
    │
    ▼
Notification Service
    │
    ▼
PostgreSQL
```

The due-soon notification service is idempotent, preventing repeated executions from generating duplicate notifications for the same user and task.

The business rules can therefore be tested synchronously without requiring Redis or a running Celery worker.

Celery is responsible for background execution, while the service layer remains responsible for the actual business logic.

---

## Notification Rules

### Task Assignment

When a task is assigned or reassigned:

```text
Task assigned
      ↓
new assignee
      ↓
TASK_ASSIGNED notification
```

No notification is created when:

- The task remains assigned to the same user
- The task has no assignee
- A user assigns the task to themselves

### Comments

When someone comments on a task, notifications may be sent to:

- The task creator
- The current task assignee

The system avoids:

- Notifying the comment author about their own comment
- Sending duplicate notifications when the creator and assignee are the same user

### Due-Soon Tasks

A task is considered due soon when:

```text
due_date > today

AND

due_date <= today + 7 days

AND

status != done

AND

assigned_to != null
```

Repeated execution does not create duplicate due-soon notifications.

---

## Local Setup

### Requirements

You need:

- Python 3.13
- PostgreSQL
- uv
- Git
- Docker Desktop
- Docker Compose

On Windows, Docker Desktop can use WSL 2 as its Linux container backend.

---

## Clone the Repository

```bash
git clone <repository-url>
cd teamflow
```

Replace `<repository-url>` with the actual repository URL.

---

## Install Dependencies

TeamFlow uses `uv` for dependency and virtual environment management.

Run:

```bash
uv sync
```

`uv` will create the project's virtual environment automatically:

```text
.venv/
```

based on:

```text
pyproject.toml
uv.lock
```

You do not need to manually create a virtual environment or use `pip install -r requirements.txt`.

---

## Environment Variables

Create a `.env` file based on `.env.example`.

Example development configuration:

```env
DJANGO_SECRET_KEY=your-local-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=teamflow
DB_USER=teamflow_user
DB_PASSWORD=your-local-database-password
DB_HOST=localhost
DB_PORT=5432

CELERY_BROKER_URL=redis://localhost:6379/0

DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SESSION_COOKIE_SECURE=False
DJANGO_CSRF_COOKIE_SECURE=False
DJANGO_SECURE_HSTS_SECONDS=0
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=False
DJANGO_SECURE_HSTS_PRELOAD=False
```

Never commit `.env` or real credentials to the repository.

Production values must be provided by the deployment environment rather than stored in source control.

---

## Production-Oriented Configuration

Security-sensitive Django settings are controlled through environment variables.

TeamFlow supports configuration for:

```text
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
DJANGO_SECURE_SSL_REDIRECT
DJANGO_SESSION_COOKIE_SECURE
DJANGO_CSRF_COOKIE_SECURE
DJANGO_SECURE_HSTS_SECONDS
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS
DJANGO_SECURE_HSTS_PRELOAD
```

This allows development and production environments to use different security policies without modifying source code.

Django deployment checks can be executed with:

```bash
uv run python manage.py check --deploy
```

A hardened production-like configuration has been validated using Django's deployment system checks.

HSTS subdomain and preload policies remain configurable because their final values depend on the production domain, HTTPS topology, and reverse-proxy configuration.

---

## PostgreSQL Setup

Create a PostgreSQL application user:

```sql
CREATE ROLE teamflow_user WITH LOGIN;
```

Set its password securely from PostgreSQL:

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

The `CREATEDB` permission is useful for local testing because pytest/Django creates a temporary database such as:

```text
test_teamflow
```

This permission should not normally be granted to the application's database user in production.

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

Expected result:

```text
System check identified no issues
```

Verify that model changes have corresponding migrations:

```bash
uv run python manage.py makemigrations --check --dry-run
```

Expected result:

```text
No changes detected
```

---

## Docker Services

The local Docker Compose stack currently contains:

```text
web
redis
celery-worker
celery-beat
```

The web container runs Django through Gunicorn.

Redis provides the Celery message broker.

The worker executes asynchronous jobs.

Celery Beat schedules periodic jobs.

Start the complete stack with:

```bash
docker compose up -d
```

Check the status:

```bash
docker compose ps
```

Validate the Compose configuration without printing resolved environment values:

```bash
docker compose config --quiet
```

Stop all containers with:

```bash
docker compose down
```

---

## Redis

Redis is used as the Celery message broker.

Test Redis:

```bash
docker compose exec redis redis-cli ping
```

Expected response:

```text
PONG
```

Redis is mapped locally to:

```text
127.0.0.1:6379
```

rather than being unnecessarily exposed to the entire local network.

---

## Celery Worker

Celery is integrated with Django through:

```text
config/celery.py
```

Celery automatically discovers tasks defined inside Django applications.

The notifications application defines:

```text
notifications.notify_due_soon_tasks
```

The task delegates business logic to:

```text
apps/notifications/services.py
```

instead of duplicating notification rules inside the Celery task itself.

The worker runs as a Linux container through Docker Compose.

Check worker connectivity with:

```bash
docker compose exec celery-worker celery -A config inspect ping
```

A healthy worker should respond with a `pong`.

---

## Celery Beat

Celery Beat runs as a separate Docker Compose service.

It schedules:

```text
notifications.notify_due_soon_tasks
```

which is delivered through Redis and executed by the Celery worker.

This keeps scheduling and task execution as separate processes:

```text
Celery Beat
     ↓
Redis
     ↓
Celery Worker
```

Only one Beat scheduler should manage the same schedule to avoid duplicate periodic task dispatch.

---

## Gunicorn and Web Container

The Docker image uses Gunicorn as the default web server:

```text
Gunicorn
   ↓
Django WSGI
   ↓
Django REST Framework
```

Django's `runserver` remains useful for local development, but the containerized web service runs through Gunicorn to provide a production-oriented execution model.

Start the web service with:

```bash
docker compose up -d web
```

Check its logs:

```bash
docker compose logs --tail 50 web
```

The local API is exposed at:

```text
http://127.0.0.1:8000/
```

Swagger UI is available at:

```text
http://127.0.0.1:8000/api/docs/
```

---

## Run the Development Server

For development without the web container:

```bash
uv run python manage.py runserver
```

The API will be available locally at:

```text
http://127.0.0.1:8000/
```

Alternatively, run the complete containerized stack:

```bash
docker compose up -d
```

---

## Running Tests

Run the complete test suite:

```bash
uv run pytest
```

The project currently contains:

```text
201 passing tests
```

The suite covers scenarios such as:

- User registration
- JWT authentication
- Access token handling
- Refresh token rotation
- Token blacklist
- Logout
- Unauthorized access
- Team isolation
- Role-based permissions
- Membership rules
- Team ownership transfer
- Project permissions
- Project uniqueness constraints
- Task creation
- Task assignment
- Task reassignment
- Task permissions
- Task status updates
- Filtering
- Searching
- Ordering
- Pagination
- Comment creation
- Comment ownership
- Comment moderation
- Dashboard metrics
- Overdue task calculations
- Due-soon task calculations
- User notifications
- Task assignment notifications
- Comment notifications
- Due-soon notifications
- Notification idempotency
- Celery configuration
- Celery task registration
- Celery task behavior
- Celery Beat configuration
- OpenAPI schema regression tests
- ORM query regression tests for N+1 detection

The test suite runs against PostgreSQL.

Celery business logic is tested synchronously so the normal unit/integration test suite does not depend on a running Redis container or Celery worker.

---

## Database Integrity

Important business rules are also enforced at database level.

Examples include:

- A user can only belong once to a team
- A team can only have one owner
- Project names are unique inside each team

Database indexes are used for commonly queried combinations such as:

- Membership team and role
- Membership user and role
- Task project and status
- Task project and priority
- Task assignee and status
- Comment task and creation date
- Notification user and read state
- Notification user and creation date

This helps move important integrity rules closer to the database instead of relying exclusively on application code.

---

## Database Performance

Critical read endpoints include regression tests that verify the number of SQL queries does not grow linearly with the number of returned objects.

The audit currently covers:

- Teams
- Projects
- Tasks
- Comments
- Notifications
- Team dashboard

Measured results include:

```text
Tasks
1 task  → 3 queries
10 tasks → 3 queries

Comments
1 comment  → 3 queries
10 comments → 3 queries

Projects
1 project  → 2 queries
10 projects → 2 queries

Notifications
1 notification  → 1 query
10 notifications → 1 query
```

During the audit, an N+1 query issue was identified in the team list serialization.

Before optimization:

```text
1 team  → 2 queries
10 teams → 11 queries
```

After optimization:

```text
1 team  → 1 query
10 teams → 1 query
```

The issue occurred because the queryset already calculated the member count through an annotation, but the serializer executed an additional count query for each team.

The serializer now reuses the annotated value instead of issuing per-object queries.

The dashboard also remains constant at:

```text
Empty workload             → 5 queries
10 projects / 100 tasks    → 5 queries
```

These regression tests help prevent future N+1 problems from being introduced accidentally.

---

## Security Considerations

The project includes several security-oriented decisions:

- JWT-based authentication
- Authentication required by default
- Role-based authorization
- Team-based resource isolation
- Users cannot access resources from teams they do not belong to
- Foreign-resource access frequently returns `404` to avoid exposing resource existence
- Passwords are managed through Django's authentication system
- Database credentials are stored in environment variables
- Django secret keys are stored outside source control
- Application secrets are excluded from Git
- Refresh token rotation
- Refresh token blacklist
- Validation of task assignees against team membership
- Database constraints enforce important business rules
- Redis is bound to localhost in the local development configuration
- Users cannot access or modify another user's notifications
- `DEBUG` is environment-dependent
- `ALLOWED_HOSTS` is environment-dependent
- HTTPS redirect can be enabled through environment configuration
- Secure session cookies can be enabled in production
- Secure CSRF cookies can be enabled in production
- HSTS is configurable per environment
- Django deployment security checks have been validated with a hardened production-like configuration
- CI uses ephemeral credentials rather than development or production secrets

HSTS preload, subdomain HSTS, and reverse-proxy SSL headers should only be finalized after the production domain and proxy topology are known.

---

## Static Typing

The project uses type information and editor tooling to improve code quality.

Development dependencies include:

```text
django-stubs
djangorestframework-stubs
```

These improve static analysis for Django and Django REST Framework.

Where framework-generated attributes or metaclass behavior cannot be inferred correctly, localized type narrowing, casts, or narrowly scoped Pyright suppressions are preferred over disabling diagnostics globally.

Examples include:

- Narrowing optional serializer instances
- Respecting exact DRF method signatures
- Using concrete application user types
- Avoiding unsafe mutation of generic mappings
- Handling Django ORM dynamic relationships carefully

Typing changes are validated against the automated test suite to ensure they do not alter runtime behavior.

---

## Dependency Management with uv

TeamFlow uses `uv` instead of `pip + requirements.txt`.

The main dependency files are:

```text
pyproject.toml
uv.lock
```

### Install or synchronize dependencies

```bash
uv sync
```

### Install exactly the locked dependency graph

```bash
uv sync --locked
```

### Add a production dependency

```bash
uv add package-name
```

### Add a development dependency

```bash
uv add --dev package-name
```

### Remove a dependency

```bash
uv remove package-name
```

### View the dependency tree

```bash
uv tree
```

### Run Python

```bash
uv run python
```

### Run Django commands

```bash
uv run python manage.py <command>
```

### Run tests

```bash
uv run pytest
```

`uv.lock` is committed to Git so the project can reproduce a consistent dependency graph across development environments and continuous integration.

---

## Development Workflow

A typical local workflow is:

```bash
uv sync

docker compose up -d

uv run python manage.py migrate

uv run python manage.py check

uv run python manage.py spectacular --validate

uv run pytest
```

For development using Django's built-in server:

```bash
uv run python manage.py runserver
```

For the containerized production-oriented stack:

```bash
docker compose up -d
```

---

## Quality Gates

Before considering a change ready, TeamFlow can validate:

```bash
uv run python manage.py check
```

```bash
uv run python manage.py makemigrations --check --dry-run
```

```bash
uv run python manage.py spectacular --validate
```

```bash
uv run pytest
```

For production-oriented configuration:

```bash
uv run python manage.py check --deploy
```

The same core checks are enforced automatically by GitHub Actions.

---

## AI-Assisted Development

AI tools were used during development as a learning and engineering assistant for activities such as:

- Reviewing backend architecture decisions
- Discussing API and authorization design
- Exploring edge cases
- Designing testing scenarios
- Debugging implementation errors
- Debugging development environment issues
- Reviewing security considerations
- Understanding Django and Django REST Framework concepts
- Understanding PostgreSQL behavior
- Reviewing Docker and Redis integration
- Understanding Celery and background processing
- Reviewing ORM query performance
- Designing OpenAPI regression tests
- Reviewing continuous integration configuration
- Comparing implementation alternatives

AI-generated suggestions were not incorporated blindly.

Proposed solutions were reviewed, adapted to the project's architecture, verified against expected behavior, and validated through automated tests.

The project currently contains **201 passing automated tests** covering business rules, permissions, database behavior, API endpoints, dashboards, notifications, Celery integration, OpenAPI contracts, and ORM query performance.

---

## Current Status

The backend currently includes:

- JWT authentication
- Custom user model
- Teams
- Role-based memberships
- Ownership transfer
- Projects
- Tasks
- Task filters
- Task search
- Task ordering
- Task pagination
- Comments
- Comment moderation
- Comment pagination
- Team dashboard
- Personal dashboard metrics
- User notifications
- Automatic task assignment notifications
- Automatic comment notifications
- Due-soon notification processing
- Celery integration
- Containerized Celery worker
- Celery Beat scheduled jobs
- Redis broker infrastructure
- PostgreSQL integration
- Docker Compose local infrastructure
- Gunicorn web server
- Containerized Django web service
- Environment-based production configuration
- Django deployment security checks
- uv dependency management
- Static typing support for Django and DRF
- GitHub Actions continuous integration
- OpenAPI schema generation
- Swagger UI
- ReDoc
- OpenAPI regression coverage
- ORM query regression tests for N+1 detection
- Database performance audit
- **201 automated tests**

---

## Planned Improvements

Future improvements include:

- Production deployment
- Continuous deployment pipeline
- Production reverse-proxy and TLS configuration
- Production database provisioning
- Production Redis provisioning
- Production Celery worker deployment
- Production Celery Beat deployment
- Structured application logging
- Additional observability and monitoring
- Error tracking
- Health/readiness improvements for deployment environments
- Frontend client

---

## Engineering Goals

TeamFlow is intended to demonstrate more than basic CRUD operations.

The project focuses on:

- REST API design
- Relational database modeling
- Authentication
- Authorization
- Business rules
- Data isolation
- Database integrity
- Service-layer design
- Background processing
- Scheduled jobs
- Idempotency
- Automated testing
- Continuous integration
- OpenAPI contracts
- Static typing
- ORM performance
- N+1 detection and prevention
- Security
- Production-oriented configuration
- Containerization
- Maintainability
- Reproducible development environments

---

## Author

**Omar López**

Backend Developer focused on Python, Django, REST APIs, PostgreSQL, backend architecture, automated testing, asynchronous processing, and production-oriented backend engineering.