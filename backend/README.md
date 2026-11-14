# Banking API Backend

A RESTful banking API built with Python, Flask, and PostgreSQL. The project is developed inside a VS Code Dev Container using Docker Compose.

## Tech Stack

- **Language:** Python
- **Framework:** Flask
- **Database:** PostgreSQL 17
- **Database Driver:** Psycopg 3
- **Password Hashing:** Argon2
- **Authentication:** Stateful sessions with opaque tokens
- **Authorization:** Role-based access control and resource ownership checks
- **Development Environment:** VS Code Dev Containers and Docker Compose

## Project Structure

```text
project-root/
├── .devcontainer/
│   ├── devcontainer.json
│   ├── docker-compose.yml
│   └── Dockerfile
├── backend/
│   ├── app.py
│   ├── decorators.py
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
├── database/
│   ├── init/
│   │   └── schema.sql
│   └── reset-db.sh
├── .env
├── .env.example
├── .gitignore
└── requirements.txt
```

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Visual Studio Code](https://code.visualstudio.com/)
- VS Code **Dev Containers** extension

## Getting Started

### 1. Configure Environment Variables

Create a `.env` file in the project root using `.env.example` as a template.

Example:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme
POSTGRES_DB=appdb

APP_DB_USER=banking_app
APP_DB_PASSWORD=changemetoo

DB_HOST=localhost
DB_PORT=5432

SESSION_TTL_HOURS=8
```

Replace the example password with a secure local development password.

The `.env` file provides configuration to the PostgreSQL container through Docker Compose. Keep it out of version control; commit `.env.example` without real credentials.

`SESSION_TTL_HOURS` controls how long authenticated sessions remain valid. The application defaults to 8 hours and accepts values between 1 and 168.

### 2. Open the Dev Container

1. Open the project root in VS Code.
2. Ensure Docker Desktop is running.
3. Open the Command Palette with `Ctrl+Shift+P`.
4. Select **Dev Containers: Reopen in Container**.
5. Wait for the container to build and the Python dependencies to install.

The Dev Container configuration mounts the parent directory of the project into `/workspaces`. The workspace path uses `${localWorkspaceFolderBasename}`, allowing developers to use different local project folder names.

The Python application runs in the `app` service, while PostgreSQL runs in the `db` service.

### 3. Database Configuration

Docker Compose starts PostgreSQL 17 and persists database files in the named `postgres-data` volume.

The application shares the database container's network namespace through `network_mode: service:db`. Therefore, the application connects to PostgreSQL using:

```env
DB_HOST=localhost
DB_PORT=5432
```

The `backend/database/connection.py` module loads the environment configuration and provides a reusable `get_connection()` function for route handlers.

Database connections use Psycopg connection and cursor context managers to manage resource cleanup and transaction handling.

### 4. Initialize the Database

Initialize the PostgreSQL database using the project's SQL schema and initialization scripts.

The database is stored in a persistent Docker volume, so rebuilding the Dev Container does not automatically recreate the database or rerun initialization scripts.

To verify the database connection and inspect available tables, run the following inside the Dev Container:

```bash
psql -h localhost -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\dt'
```

### 5. Run the Application

From the project root inside the Dev Container:

```bash
python backend/app.py
```

Alternatively, if your terminal is already in `backend/`:

```bash
python app.py
```

The Flask application listens on `0.0.0.0:5000` so VS Code can forward port `5000` to your local machine.

The API should then be accessible at:

```text
http://localhost:5000
```

## API Endpoints

All endpoints requiring authentication expect an opaque session token in the HTTP `Authorization` header:

```text
Authorization: Bearer <session_token>
```

### Authentication

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/employees/register` | Register an employee using an invitation token |
| POST | `/auth/employees/login` | Authenticate an employee |
| POST | `/auth/customers/register` | Set up a customer password using a setup token |
| POST | `/auth/customers/login` | Authenticate a customer |
| POST | `/auth/logout` | Invalidate the current session |

Employee and customer registration use separate setup-token workflows. These tokens are generated when an employee or customer record is provisioned and are required to complete account registration.

### Employees

| Method | Endpoint | Purpose | Access |
|---|---|---|---|
| POST | `/employees` | Generate an employee registration token | Admin |
| GET | `/employees` | Retrieve all employees | Admin |
| GET | `/employees/<employee_id>` | Retrieve an employee | Employee |
| PUT | `/employees/<employee_id>` | Update an employee's username | Employee |
| DELETE | `/employees/<employee_id>` | Delete an employee | Admin |

Employees can retrieve and update their own records. Administrators can retrieve and update other employees.

Employee registration tokens contain the assigned employee role, which is retrieved during registration rather than supplied by the registering user.

### Customers

| Method | Endpoint | Purpose | Access |
|---|---|---|---|
| POST | `/customers` | Create a customer and generate a setup token | Employee |
| GET | `/customers` | Retrieve all customers | Employee |
| GET | `/customers/<customer_id>` | Retrieve a customer | Employee or owning customer |
| PUT/PATCH | `/customers/<customer_id>` | Update customer information | Employee |
| DELETE | `/customers/<customer_id>` | Delete a customer | Employee or owning customer |

Customer creation generates a one-time setup token used to establish the customer's password through the registration endpoint.

Customer records include personal information such as SSN. API responses mask SSNs, exposing only the last four digits.

### Accounts

| Method | Endpoint | Purpose | Access |
|---|---|---|---|
| POST | `/accounts` | Create an account | Employee |
| GET | `/accounts` | Retrieve all accounts | Employee |
| GET | `/accounts/<account_id>` | Retrieve an account | Employee or owning customer |
| PUT | `/accounts/<account_id>` | Update an account's customer association | Employee |
| DELETE | `/accounts/<account_id>` | Delete an account | Employee |
| POST | `/accounts/<account_id>/deposit` | Deposit funds | Employee or owning customer |
| POST | `/accounts/<account_id>/withdraw` | Withdraw funds | Employee or owning customer |

Account numbers are masked in API responses, exposing only the last four digits.

Deposit and withdrawal operations validate monetary amounts and enforce account balance limits. Withdrawals use an atomic database update to prevent concurrent requests from overdrawing an account.

## Authentication and Authorization

The authentication system uses stateful sessions stored in PostgreSQL.

- Passwords are hashed with Argon2 rather than stored in plaintext or encrypted reversibly.
- Successful login generates a cryptographically random session token.
- Only a SHA-256 hash of the session token is stored in the database.
- Sessions have an expiration time controlled by `SESSION_TTL_HOURS`.
- Session records can be invalidated server-side, allowing sessions to be revoked.
- Customer and employee sessions are associated with their respective database records.

Authenticated routes use shared decorators to validate sessions and enforce access requirements.

The application supports two employee roles:

- **Teller:** Employee-level access to banking operations.
- **Admin:** Administrative access to employee management and other protected operations.

Customer access is restricted to resources associated with their own customer record. Employees can access customer and account resources according to their permissions.

## Development Notes

- Database connections are created through the shared `get_connection()` function.
- Route modules are organized into Flask Blueprints.
- The routes package exports its Blueprints through `__all__`, which `app.py` uses to register them automatically.
- Authentication and authorization decorators are centralized in `decorators.py`.
- Database exceptions and unexpected application errors are handled centrally in `app.py`.
- Database operations use parameterized SQL queries.
- Docker Compose manages the application development environment and PostgreSQL service.
- The named `postgres-data` volume persists database data across container restarts.

## Security Considerations

This project is for development and learning purposes. Before deploying a banking application, implement and test appropriate protections, including:

- HTTPS and secure secret management.
- Authentication and role-based authorization.
- Customer and account-level access controls.
- Input validation and consistent error handling.
- Protection against unauthorized balance changes and invalid transactions.
- Session expiration, logout, and revocation.
- Transaction history and audit logging.
- Database backups, monitoring, and automated tests.

Never commit `.env` files, production credentials, or real customer information to version control.