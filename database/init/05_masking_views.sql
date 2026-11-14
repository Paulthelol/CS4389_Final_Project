-- Masked read-only views of sensitive fields for the backend to query.
-- security_invoker makes the querying user's RLS policies apply to the underlying tables.

-- SSN shown as ***-**-1234; password_hash is left out.
CREATE VIEW customers_masked
WITH (security_invoker = true) AS
SELECT
    customer_id,
    first_name,
    last_name,
    '***-**-' || right(ssn, 4) AS ssn,
    email
FROM customers;

-- Account number shown as *****1234.
CREATE VIEW accounts_masked
WITH (security_invoker = true) AS
SELECT
    account_id,
    customer_id,
    '*****' || right(account_number, 4) AS account_number,
    balance
FROM accounts;

GRANT SELECT ON customers_masked, accounts_masked TO banking_app;
