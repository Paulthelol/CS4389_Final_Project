# Banking API Backend

A Flask REST API backed by PostgreSQL for managing employees, customers, and accounts. This project is being developed as a learning project, with an emphasis on API design, database integration, and authentication.

## Technology Stack

- **Language:** Python
- **Web framework:** Flask
- **Database:** PostgreSQL 17
- **Database driver:** Psycopg 3
- **Password hashing:** Argon2
- **Authentication:** Stateful sessions using opaque bearer tokens
- **Development environment:** VS Code Dev Containers and Docker Compose

## Project Structure

This README is located in `backend/`. The Dev Container configuration, environment files, and dependency list are stored at the project root.

```text
project-root/
├── .devcontainer/
│   ├── devcontainer.json
│   ├── docker-compose.yml
│   └── Dockerfile
├── backend/
│   ├── app.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── employees.py
│   │   ├── customers.py
│   │   └── accounts.py
│   └── README.md
├── .env
├── .env.example
├── .gitignore
└── requirements.txt
```

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Visual Studio Code](https://code.visualstudio.com/)
- The **Dev Containers** extension for VS Code

## Setup

### 1. Configure environment variables

From the project root (the directory containing `backend/`), create a `.env` file. Use the root-level `.env.example` as a template:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme
POSTGRES_DB=appdb
DB_HOST=localhost
DB_PORT=5432
SESSION_TTL_HOURS=#
```

Replace placeholder values with your local development settings. Do not commit `.env` or real credentials to version control.

### 2. Open the project in the Dev Container

1. Open the project root folder in VS Code, not just the `backend/` subfolder.
2. Open the Command Palette.
3. Select **Dev Containers: Reopen in Container**.
4. Wait for the application and PostgreSQL services to start and for Python dependencies to install.

The Dev Container opens the project root as the workspace. Docker Compose mounts the parent directory into `/workspaces`, allowing the workspace path to use the local project folder's name.

The application shares the database service's network namespace. Therefore, the application connects to PostgreSQL using `localhost` on port `5432`.

### 3. Initialize the database

Create the required PostgreSQL tables before using the API. The application expects these tables:

- **employees** — employee usernames, password hashes, and roles (`teller` or `admin`).
- **customers** — customer information.
- **accounts** — accounts associated with customers, including account numbers and balances.
- **sessions** — active session records, including employee associations, token hashes, and expiration timestamps.

The database uses a named Docker volume (`postgres-data`) to persist PostgreSQL data across normal container restarts and recreation. Removing the volume will delete the stored database data.

### 4. Run the Flask application

From the project root inside the Dev Container:

```bash
python backend/app.py
```

Alternatively, if your terminal's current directory is `backend/`, run:

```bash
python app.py
```

The Flask development server should listen on `0.0.0.0:5000` so it can be accessed through the forwarded port. Use Flask's debug server for local development only.

## API Endpoints

The authentication endpoints below are implemented. CRUD endpoints for employees, customers, and accounts are **in progress** and should not be considered complete until their route handlers and required checks have been implemented and tested.

| Method | Endpoint | Status | Description |
|---|---|---|---|
| `POST` | `/auth/register` | Implemented | Register an employee account with the default `teller` role. |
| `POST` | `/auth/login` | Implemented | Verify credentials and create a session. |
| `POST` | `/auth/logout` | Implemented | Delete the session associated with a supplied bearer token. |
| `GET` | `/employees` | In progress | Retrieve employee records. |
| `GET` | `/employees/<employee_id>` | In progress | Retrieve an employee by ID. |
| `POST` | `/employees` | In progress | Create an employee record, subject to authorization rules. |
| `PUT` / `PATCH` | `/employees/<employee_id>` | In progress | Update an employee record. |
| `DELETE` | `/employees/<employee_id>` | In progress | Delete an employee record. |
| `GET` | `/customers` | In progress | Retrieve customer records. |
| `GET` | `/customers/<customer_id>` | In progress | Retrieve a customer by ID. |
| `POST` | `/customers` | In progress | Create a customer record. |
| `PUT` / `PATCH` | `/customers/<customer_id>` | In progress | Update a customer record. |
| `DELETE` | `/customers/<customer_id>` | In progress | Delete a customer record. |
| `GET` | `/accounts` | In progress | Retrieve account records. |
| `GET` | `/accounts/<account_id>` | In progress | Retrieve an account by ID. |
| `POST` | `/accounts` | In progress | Create an account associated with a customer. |
| `PUT` / `PATCH` | `/accounts/<account_id>` | In progress | Update an account record. |
| `DELETE` | `/accounts/<account_id>` | In progress | Delete an account record. |

The CRUD paths above describe the intended API and may change during implementation. Route availability depends on the current code.

## Authentication Design

The API uses stateful sessions rather than JWTs.

- **Password storage:** Employee passwords are hashed with Argon2. Plaintext passwords should never be stored.
- **Session tokens:** Login generates a cryptographically random opaque token. The raw token is returned to the client, while a SHA-256 hash of the token is stored in PostgreSQL.
- **Session expiration:** The `SESSION_TTL_HOURS` environment variable controls the session lifetime.
- **Logout:** The logout endpoint deletes the session matching the supplied bearer token. Repeating a logout request with a syntactically valid bearer token is designed to be idempotent.

### Current authentication limitation

The shared authentication decorator and role-based authorization checks for protected resources have **not yet been implemented**. Although login creates sessions and logout deletes them, protected API resources do not yet consistently validate session tokens or enforce expiration and role permissions. Do not assume the planned CRUD endpoints are protected.

## Development Status

### Implemented

- VS Code Dev Container configuration with Docker Compose.
- PostgreSQL service and reusable database connection function.
- Employee registration with password hashing.
- Employee login and session creation.
- Logout by deleting a session.

### In progress

- CRUD operations for employees, customers, and accounts.
- Shared authentication decorator for session validation.
- Role-based authorization for protected endpoints.
- Validation, error handling, and endpoint testing.

## Security Notes

This is a development and learning project, not a production banking system. Before using it with real users or sensitive information, additional work would be required, including:

- Enforcing authentication and authorization on protected endpoints.
- Using HTTPS in deployed environments and securely handling session tokens.
- Adding request validation, rate limiting, and appropriate error handling.
- Applying least-privilege database permissions.
- Testing transaction integrity, access controls, and failure cases.
- Establishing secure logging, backups, monitoring, and secret management.

Keep `.env` out of version control and use placeholder values in `.env.example`. Do not use real credentials or customer information in development data.
