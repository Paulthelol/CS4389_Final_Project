\getenv app_db_password APP_DB_PASSWORD

SELECT format(
    'CREATE ROLE banking_app LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS',
    :'app_db_password'
)
WHERE NOT EXISTS (
    SELECT 1
    FROM pg_roles
    WHERE rolname = 'banking_app'
)
\gexec

SELECT format(
    'GRANT CONNECT ON DATABASE %I TO banking_app',
    current_database()
)
\gexec

GRANT USAGE ON SCHEMA public TO banking_app;

GRANT SELECT, INSERT, UPDATE, DELETE
ON employees, customers, accounts, transactions, sessions,
   customer_setup_tokens
TO banking_app;

GRANT USAGE, SELECT
ON ALL SEQUENCES IN SCHEMA public
TO banking_app;
