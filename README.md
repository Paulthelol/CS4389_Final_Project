# CS4389 - Database Security in Web-Based Banking Applications

A banking application with a React/Vite frontend, a Flask backend, and PostgreSQL.

Languages: Python, JavaScript/JSX, SQL/PL/pgSQL, HTML, CSS, and Bash.

## Requirements

- Windows, macOS, or Linux with Docker configured for Linux containers and
  Docker Compose 2.24 or newer.
- For the host demo: Python 3.14, Node.js 24, and a browser. The development
  container workflow supplies Python, Node.js, and PostgreSQL 17.
- Python dependencies are listed in [requirements.txt](requirements.txt);
  frontend dependencies are listed in [frontend/package.json](frontend/package.json).
  The commands below install both.

## Class Demo Quickstart

The demo uses Docker Desktop, Python, and Node.js 24. Open Windows
PowerShell in the repository root and start both demo databases and Vite.

```powershell
docker compose -f .devcontainer/docker-compose.demo-db.yml up -d --wait
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm.cmd --prefix frontend ci
npm.cmd --prefix frontend run dev -- --host 127.0.0.1
```

In a second host PowerShell terminal at the repository root, start Flask against
the **insecure database comparison** first. Flask authentication and account
ownership checks are enabled in both runs.

```powershell
$env:DEMO_MODE = 'true'
$env:API_SECURITY_ENABLED = 'true'
$env:DB_HOST = '127.0.0.1'
$env:DB_PORT = '55432'
$env:DB_ACCESS_MODE = 'superuser'
.\.venv\Scripts\python.exe -m flask --env-file .env.example --app backend/app.py:create_app run --host 127.0.0.1 --port 5000
```

For the fully insecure class-demo mode, set
`$env:API_SECURITY_ENABLED = 'false'` instead. The website will detect this
setting, open directly in the employee interface as a demo administrator, and
provide the three intentionally vulnerable search endpoints under
**Run database demo searches**. See [DEMO.md](DEMO.md) for the full walkthrough.

Open [localhost:5173](http://127.0.0.1:5173). Sign in as a customer with
`alice@example.com` / `alice`, or choose **Employee Login** and sign in with
`admin1` / `admin1`.

To switch to the **secure database**, press **Ctrl+C** in the Flask terminal.
Run these commands in that same terminal, refresh the browser, and sign in.

```powershell
$env:DEMO_MODE = 'false'
$env:API_SECURITY_ENABLED = 'true'
$env:DB_PORT = '55431'
$env:DB_ACCESS_MODE = 'appuser'
.\.venv\Scripts\python.exe -m flask --env-file .env.example --app backend/app.py:create_app run --host 127.0.0.1 --port 5000
```

Vite and both databases stay up during the switch.

When finished, stop Flask and Vite with **Ctrl+C**. Run
`docker compose -f .devcontainer/docker-compose.demo-db.yml down` to remove
the demo containers and discard their temporary data.


## Development container

Requirements: Docker with Compose 2.24 or newer, VS Code, and the Dev Containers
extension. Windows users should run Docker Desktop with Linux containers.

1. Open this repository in VS Code.
2. Optionally copy `.env.example` to `.env` to override the local database settings.
   The example environment values work out of the box for development.
3. Run **Dev Containers: Reopen in Container** (or **Rebuild Container** after
   changing the container configuration).
4. Wait for the setup command to install Python and frontend dependencies.

The container provides: Python 3.14, Node.js 24, and PostgreSQL 17. PostgreSQL data
and container frontend dependencies use separate named volumes. The app and
database share a network namespace, so Flask connects to PostgreSQL at
`localhost:5432`. The database is not published to the host.

PostgreSQL automatically runs the scripts in [database/init/](database/init/)
when its data volume is first initialized, creating the schema, roles, policies,
views, triggers, and demo users. Other than first initialization, rebuiliding or recreating containers with existing data does NOT rerun the database setup scripts.

Start the frontend from the repository root:

```sh
npm --prefix frontend run dev
```

Alternatively run:

```sh
cd frontend
npm run dev
```

In another container terminal, start Flask:

```sh
cd backend
python -m flask --app app:create_app run --debug --host 0.0.0.0 --port 5000
```

Open http://localhost:5173. Ports 5173 (Vite), 4173 (build preview), and 5000
(Flask) are forwarded by the container. Servers are started manually.

If you change PostgreSQL credentials after its data volume is initialized,
update the database credentials too; changing `.env` does not alter existing
database users.

## Local development WIHTOUT Docker

Install Node.js 24, Python, and PostgreSQL 17. Copy `.env.example` to `.env`,
configure it for your local PostgreSQL database, then run from the repository root:

```sh
python -m pip install -r requirements.txt
npm --prefix frontend ci
npm --prefix frontend run dev
```

For this non-Docker setup, create the database named by `POSTGRES_DB` and run
the scripts in [database/init/](database/init/) in filename order using `psql`
as a PostgreSQL administrator. Set `POSTGRES_APP_PASSWORD` in the `psql` process's
environment to match `.env` before running `04_roles.sql`.

Start Flask in a second terminal using the command above. See
[`frontend/README.md`](frontend/README.md) for structure, build, lint, and proxy details.

## Test credentials

Fresh databases include these synthetic users from
[the seed data](database/init/02_demo_data.sql). Choose **Employee Login** for
administrator and teller accounts.

| Role | Email / username | Password |
| --- | --- | --- |
| Customer | `alice@example.com` | `alice` |
| Customer | `bob@example.com` | `bob` |
| Administrator | `admin1` | `admin1` |
| Teller | `teller1` | `teller1` |
| Teller | `teller2` | `teller2` |

## Limitations and incomplete features

- This is a local demo. HTTPS, multi-factor authentication, and login
  rate limiting are not implemented.
- Demo search routes are intentionally vulnerable when `DEMO_MODE=true`.
  Setting `API_SECURITY_ENABLED=false` also bypasses authentication in demo mode.
- Demo database data is NOT preserved when its containers are removed.
- Account-to-account transfers and loans are not implemented.
