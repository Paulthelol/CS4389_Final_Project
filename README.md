# CS4389 - Database Security in Web-Based Banking Applications

A banking application with a React/Vite frontend, a Flask backend, and PostgreSQL.

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
