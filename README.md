# CS4389 - Database Security in Web-Based Banking Applications

What should go in this document:
- OS requirements
- Programming language(s) used
- Required software and dependencies
- Installation instructions
- Commands to execute the program
- Login credentials for testing
- Current incomplete features

## Database Installation Instructions
1. Install Docker Desktop (no need to install Postgres separately)
2. Start the database
    - From the project root:
        ```sh
        docker compose up -d
        ```
3. Connect to PostgreSQL
    ```sh
    docker exec -it bank-db psql -U postgres -d bank_demo
    ```
4. Verify the tables were created:
    ```sh
    \dt
    ```

When needed:
- Stop the database
    ```sh
    docker compose down
    ```
- Reset the database (`-v` deletes then rebuilds data)
    ```sh
    docker compose down -v
    docker compose up -d
    ```