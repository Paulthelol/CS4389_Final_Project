FROM mcr.microsoft.com/devcontainers/python:3-3.14-trixie

ENV PYTHONUNBUFFERED=1

# Install PostgreSQL client to run psql commands from the devcontainer
RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*