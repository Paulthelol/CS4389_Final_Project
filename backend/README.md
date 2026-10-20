# Banking API Backend

A RESTful banking API built with Python, Flask, and PostgreSQL. The project is developed inside a VS Code Dev Container using Docker Compose.

## Tech Stack

- **Language:** Python
- **Framework:** Flask
- **Database:** PostgreSQL 17
- **Database Driver:** Psycopg 3
- **Password Hashing:** Argon2
- **Authentication:** Stateful sessions with opaque tokens
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
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py
│   └── routes/
│       ├── __init__.py
│       ├── auth.py
│       ├── employees.py
│       ├── customers.py
│       └── accounts.py
├── .env
├── .env.example
├── requirements.txt
└── README.md
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

DB_HOST=localhost
DB_PORT=5432

SESSION_TTL_HOURS=#
```

Replace the example password with a secure local development password.

The `.env` file provides configuration to the PostgreSQL container through Docker Compose. Keep it out of version control; commit `.env.example` without real credentials.

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

The `database/connection.py` module loads the environment configuration and provides a reusable `get_connection()` function for route handlers.

### 4. Initialize the Database

Initialize the PostgreSQL database with the tables required by the application.

The database schema includes:

- **`employees`** — employee credentials and roles (`teller` or `admin`).
- **`customers`** — customer information.
- **`accounts`** — customer-linked accounts and balances.
- **`sessions`** — active session records, token hashes, and expiration timestamps.

Ensure all required tables exist before testing the corresponding API endpoints.

### 5. Run the Application

From the project root inside the Dev Container:

```bash
python backend/app.py
```

Alternatively, if your terminal is already in `backend/`:

```bash
python app.py
```

Configure Flask to listen on `0.0.0.0:5000` so VS Code can forward port `5000` to your local machine.

The API should then be accessible at:

```text
http://localhost:5000
```

## API Endpoints

The following endpoints represent the planned API structure. Verify each route's implementation before relying on it.

| Resource | Method | Endpoint | Purpose |
|---|---|---|---|
| Authentication | POST | `/auth/register` | Register an employee account |
| Authentication | POST | `/auth/login` | Authenticate an employee |
| Authentication | POST | `/auth/logout` | Invalidate the current session |
| Employees | GET | `/employees` | Retrieve employees |
| Employees | GET | `/employees/<id>` | Retrieve an employee |
| Employees | POST | `/employees` | Create an employee |
| Employees | PUT/PATCH | `/employees/<id>` | Update an employee |
| Employees | DELETE | `/employees/<id>` | Delete an employee |
| Customers | GET | `/customers` | Retrieve customers |
| Customers | GET | `/customers/<id>` | Retrieve a customer |
| Customers | POST | `/customers` | Create a customer |
| Customers | PUT/PATCH | `/customers/<id>` | Update a customer |
| Customers | DELETE | `/customers/<id>` | Delete a customer |
| Accounts | GET | `/accounts` | Retrieve accounts |
| Accounts | GET | `/accounts/<id>` | Retrieve an account |
| Accounts | POST | `/accounts` | Create an account |
| Accounts | PUT/PATCH | `/accounts/<id>` | Update an account |
| Accounts | DELETE | `/accounts/<id>` | Delete an account |

## Authentication Design

The authentication system uses stateful sessions stored in PostgreSQL.

- Passwords are hashed with Argon2 rather than stored in plaintext or encrypted reversibly.
- Successful login generates a cryptographically random session token.
- Only a SHA-256 hash of the session token is stored in the database.
- Sessions have an expiration time controlled by `SESSION_TTL_HOURS`.
- Session records can be invalidated server-side, allowing sessions to be revoked.

Authenticated endpoints should validate session tokens and enforce employee roles and permissions before granting access.

## Development Notes

- Database connections are created through the shared `get_connection()` function.
- Route modules are organized into Flask Blueprints.
- The routes package automatically discovers eligible Blueprint objects from modules directly inside `backend/routes/`.
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
- Database backups, logging, monitoring, and automated tests.

Never commit `.env` files, production credentials, or real customer information to version control.
