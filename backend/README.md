# Banking API Backend

A RESTful banking API built with Python, Flask, and PostgreSQL. The project is developed inside a VS Code Dev Container using Docker Compose.

## Tech Stack

- **Language:** Python
- **Framework:** Flask
- **Database:** PostgreSQL 17
- **Database Driver:** Psycopg 3
- **Password Hashing:** Argon2
- **Authentication:** Stateful sessions with opaque bearer tokens
- **Authorization:** Role-based access control, resource ownership checks, and PostgreSQL Row-Level Security (RLS)
- **Database Security:** Restricted application database role and security-invoker masking views
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
│   │   ├── 01_schema.sql
│   │   ├── 02_demo_data.sql
│   │   ├── 03_rls.sql
│   │   ├── 04_roles.sql
│   │   └── 05_masking_views.sql
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
# Demo configurations
DEMO_MODE=true
API_SECURITY_ENABLED=true
DB_ACCESS_MODE=appuser

# PostgreSQL superuser credentials
POSTGRES_USER=postgres
POSTGRES_PASSWORD=changeme

# Restricted application database credentials
POSTGRES_APP_USER=banking_app
POSTGRES_APP_PASSWORD=changemetoo

# Database connection
POSTGRES_DB=appdb
DB_HOST=localhost
DB_PORT=5432

# Session configuration
SESSION_TTL_HOURS=8
```

Replace the example passwords with secure local development passwords. Use different passwords for the PostgreSQL superuser and application database role.

The environment variables control the following settings:

| Variable | Description |
|---|---|
| `DEMO_MODE` | Enables or disables demo-specific application behavior and data |
| `API_SECURITY_ENABLED` | Enables or disables API authentication and authorization enforcement |
| `DB_ACCESS_MODE` | Selects the database connection credentials: `appuser` or `superuser` |
| `POSTGRES_USER` | PostgreSQL administrative username |
| `POSTGRES_PASSWORD` | PostgreSQL administrative password |
| `POSTGRES_APP_USER` | Restricted application database username |
| `POSTGRES_APP_PASSWORD` | Restricted application database password |
| `POSTGRES_DB` | PostgreSQL database name |
| `DB_HOST` | Database hostname |
| `DB_PORT` | Database port |
| `SESSION_TTL_HOURS` | Authenticated session lifetime in hours |

`DB_ACCESS_MODE` supports two configurations:

- **`appuser`:** Uses the restricted `banking_app` role. This role is configured without superuser privileges or `BYPASSRLS`, allowing PostgreSQL row-level security policies to apply.
- **`superuser`:** Uses the PostgreSQL administrative account. This account bypasses row-level security and should be reserved for database administration and controlled development/testing.

`API_SECURITY_ENABLED` and `DB_ACCESS_MODE` are independent settings. For example, API security can be enabled while using the application database role, allowing both application-level authorization and database-level RLS enforcement.

`SESSION_TTL_HOURS` controls how long authenticated sessions remain valid. The application defaults to 8 hours and accepts values between 1 and 168.

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

The application shares the database container's network namespace through:

```yaml
network_mode: service:db
```

Therefore, the application connects to PostgreSQL using:

```env
DB_HOST=localhost
DB_PORT=5432
```

The `backend/database/connection.py` module provides reusable database connection functions:

- **`get_connection()`**: Creates a connection using the credentials selected by `DB_ACCESS_MODE`.
- **`get_authenticated_connection()`**: Creates a connection and establishes transaction-local PostgreSQL session settings identifying the authenticated user's role and ID.
- **`get_pre_auth_connection()`**: Creates a connection with a designated administrative RLS context for operations that occur before authentication or when API security is disabled.

Authenticated database connections establish the following PostgreSQL settings:

- `app.current_role`
- `app.current_employee_id`
- `app.current_customer_id`

These settings allow PostgreSQL RLS policies to determine which records the current request can access.

Database connections use Psycopg connection and cursor context managers to manage resource cleanup and transaction handling.

### 4. Initialize the Database

The database initialization scripts are located in `database/init/` and are executed in the following order:

| Script | Purpose |
|---|---|
| `01_schema.sql` | Creates the database tables, constraints, and indexes |
| `02_demo_data.sql` | Inserts demonstration employees and customers |
| `03_rls.sql` | Enables row-level security and defines access policies |
| `04_roles.sql` | Creates and configures the restricted application database role and grants permissions |
| `05_masking_views.sql` | Creates masked customer and account views |

The database schema includes employees, customers, accounts, transactions, sessions, and registration setup-token tables.

PostgreSQL initialization scripts are executed when the database volume is first initialized. Rebuilding the Dev Container does not automatically recreate the database or rerun initialization scripts.

To verify the database connection and inspect available tables, run the following inside the Dev Container:

```bash
psql -h localhost -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\dt'
```

To inspect the configured views:

```bash
psql -h localhost -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\dv'
```

The `database/reset-db.sh` script can be used to reset the development database and rerun the initialization scripts. **This operation deletes the existing PostgreSQL data volume and its contents.**

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

```http
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

Employee and customer registration use separate setup-token workflows.

Employee registration tokens are generated when an administrator provisions an employee account. The token contains the assigned employee role, which is retrieved during registration rather than supplied by the registering user.

Customer setup tokens are generated when an employee creates a customer record. Customers use these one-time tokens to establish their passwords.

### Employees

| Method | Endpoint | Purpose | Access |
|---|---|---|---|
| POST | `/employees` | Generate an employee registration token | Admin |
| GET | `/employees` | Retrieve all employees | Admin |
| GET | `/employees/<employee_id>` | Retrieve an employee | Employee |
| PUT | `/employees/<employee_id>` | Update an employee's username | Employee |
| DELETE | `/employees/<employee_id>` | Delete an employee | Admin |

Employees can retrieve and update their own records. Administrators can retrieve and manage other employees.

### Customers

| Method | Endpoint | Purpose | Access |
|---|---|---|---|
| POST | `/customers` | Create a customer and generate a setup token | Employee |
| GET | `/customers` | Retrieve all customers | Employee |
| GET | `/customers/<customer_id>` | Retrieve a customer | Employee or owning customer |
| PUT/PATCH | `/customers/<customer_id>` | Update customer information | Employee |
| DELETE | `/customers/<customer_id>` | Delete a customer | Employee or owning customer |

Customer creation generates a one-time setup token used to establish the customer's password through the registration endpoint.

Customer records include personal information such as SSN. API responses use the `customers_masked` database view, exposing only the last four digits of an SSN. Password hashes are excluded from the view.

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

Account numbers are masked in API responses using the `accounts_masked` database view, exposing only the last four digits.

Deposit and withdrawal operations validate monetary amounts and enforce account balance limits. Withdrawals use an atomic database update to prevent concurrent requests from overdrawing an account.

Deposits and withdrawals record a transaction in the same database operation as the balance change. Insecure demo requests are marked `is_demo` and have no employee or customer actor.

## Authentication and Authorization

### Session Authentication

The authentication system uses stateful sessions stored in PostgreSQL.

- Passwords are hashed with Argon2 rather than stored in plaintext or encrypted reversibly.
- Successful login generates a cryptographically random session token.
- Only a SHA-256 hash of the session token is stored in the database.
- Sessions have an expiration time controlled by `SESSION_TTL_HOURS`.
- Session records can be invalidated server-side, allowing sessions to be revoked.
- Customer and employee sessions are associated with their respective database records.

Authenticated routes use shared decorators to validate sessions and enforce access requirements.

### Application-Level Authorization

The application supports two employee roles:

- **Teller:** Employee-level access to customer and account operations.
- **Admin:** Administrative access, including employee management.

Customer access is restricted to resources associated with their own customer record. Employees can access customer and account resources according to their permissions.

Authorization checks are performed using the authenticated identity established by the session-validation decorators. Resource ownership is not determined from user-supplied identity fields in request bodies or query parameters.

### Database-Level Authorization

PostgreSQL Row-Level Security provides an additional layer of access control independently of the Flask route authorization logic.

RLS is enabled on:

- `employees`
- `customers`
- `accounts`
- `transactions`

The policies use transaction-local PostgreSQL settings established by `get_authenticated_connection()` to determine the current user's role and identity.

The policies enforce the following access rules:

| Table | Admin | Teller | Customer |
|---|---|---|---|
| Employees | All records | Own employee record | No access |
| Customers | All records | All records | Own customer record |
| Accounts | All records | All records | Own accounts |
| Transactions | All records | All records | Transactions associated with own accounts |

The application connects using the restricted `banking_app` database role by default. This role does not have superuser privileges or the `BYPASSRLS` attribute, allowing RLS policies to enforce record-level access.

The PostgreSQL superuser bypasses RLS. Consequently, using `DB_ACCESS_MODE=superuser` is not suitable for validating database-level access restrictions.

### Database Masking Views

The database provides two security-invoker views for retrieving records containing sensitive information:

- **`customers_masked`**: Returns customer information with SSNs masked and password hashes excluded.
- **`accounts_masked`**: Returns account information with account numbers masked.

Both views use PostgreSQL's `security_invoker` option so that the querying user's underlying table permissions and RLS policies apply.

The customer and account route modules use these views for read operations and API response data rather than retrieving raw sensitive values and masking them in Python.

## Development Notes

- Database connections are managed through the shared functions in `backend/database/connection.py`.
- Route modules use connection helpers to establish the appropriate authenticated RLS context.
- Route modules are organized into Flask Blueprints.
- The routes package exports its Blueprints through `__all__`, which `app.py` uses to register them automatically.
- Authentication and authorization decorators are centralized in `decorators.py`.
- Database exceptions and unexpected application errors are handled centrally in `app.py`.
- Database operations use parameterized SQL queries.
- Psycopg context managers handle connection cleanup and transaction boundaries.
- The database initialization scripts are maintained separately from the Flask application.
- Docker Compose manages the application development environment and PostgreSQL service.
- The named `postgres-data` volume persists database data across container restarts.