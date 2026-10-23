#!/usr/bin/env bash

# Rebuilding the Dev Container does not reset the database volume, so
# use this script after changing the schema or initialization data.
# Run from a host terminal, NOT inside the Dev Container (this script recreates the container).
#
# Usage: ./database/reset-db.sh

set -euo pipefail

# Resolve paths relative to this script, not the terminal's location.
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/.devcontainer/docker-compose.yml"

# Find running database containers associated with this project.
DB_CONTAINER="$(docker ps -q \
    --filter "label=com.docker.compose.service=db" \
    --filter "label=com.docker.compose.project.working_dir=$PROJECT_ROOT/.devcontainer")"

if [[ -z "$DB_CONTAINER" ]]; then
    echo "Database container not found."
    exit 1
fi

# Make sure we found exactly one container.
if [[ "$(echo "$DB_CONTAINER" | wc -l)" -ne 1 ]]; then
    echo "Multiple matching database containers found."
    exit 1
fi

# Get the actual Compose project name used by VS Code.
PROJECT_NAME="$(docker inspect "$DB_CONTAINER" \
    --format '{{index .Config.Labels "com.docker.compose.project"}}')"

compose() {
    docker compose \
        -p "$PROJECT_NAME" \
        -f "$COMPOSE_FILE" \
        "$@"
}

if [[ -z "$DB_CONTAINER" ]]; then
    echo "Database container not found. Start the project first."
    exit 1
fi

# Find the exact Docker volume holding PostgreSQL data.
DB_VOLUME="$(docker inspect "$DB_CONTAINER" \
    --format '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}{{.Name}}{{end}}{{end}}')"

if [[ -z "$DB_VOLUME" ]]; then
    echo "PostgreSQL data volume not found."
    exit 1
fi

echo "WARNING: This will permanently delete PostgreSQL data in:"
echo "  $DB_VOLUME"
read -r -p "Continue? [y/N] " confirm

if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Cancelled."
    exit 0
fi

# Stop both containers because app shares db's network namespace.
compose stop app db
compose rm -f app db

# Delete only the PostgreSQL data volume.
docker volume rm "$DB_VOLUME"

# Recreate containers. PostgreSQL runs initialization scripts automatically.
compose up -d

echo "Database reset initiated."
echo "Check initialization output with:"
echo "  docker compose -f .devcontainer/docker-compose.yml logs db"
