# CS4389 - Database Security in Web-Based Banking Applications

A banking application with a React/Vite frontend, a Flask backend, and PostgreSQL.

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

## Local development

Install Node.js 24, Python, and PostgreSQL 17. Copy `.env.example` to `.env`,
configure it for your local PostgreSQL database, then run from the repository root:

```sh
python -m pip install -r requirements.txt
npm --prefix frontend ci
npm --prefix frontend run dev
```

Start Flask in a second terminal using the command above. See
[`frontend/README.md`](frontend/README.md) for structure, build, lint, and proxy details.

## Additional Notes
- OS requirements
- Programming language(s) used
- Required software and dependencies
- Installation instructions
- Commands to execute the program
- Login credentials for testing
- Current incomplete features
- : )
