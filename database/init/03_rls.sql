-- The backend sets app.current_user_id and app.current_role
-- as transaction-local settings based on the authenticated session.

-- Users can access their own identity record; administrators can access all users.
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_access ON users
    FOR ALL
    USING (
        current_setting('app.current_role', true) = 'admin'
        OR user_id = NULLIF(
            current_setting('app.current_user_id', true), ''
        )::bigint
    );

-- Tellers can access their own employee profile; administrators can access all.
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;

CREATE POLICY employee_access ON employees
    FOR ALL
    USING (
        current_setting('app.current_role', true) = 'admin'
        OR (
            current_setting('app.current_role', true) = 'teller'
            AND employees.user_id = NULLIF(
                current_setting('app.current_user_id', true), ''
            )::bigint
        )
    );

-- Customers can access their own profile; tellers and administrators can access all customers.
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

CREATE POLICY customer_access ON customers
    FOR ALL
    USING (
        current_setting('app.current_role', true) IN ('admin', 'teller')
        OR (
            current_setting('app.current_role', true) = 'customer'
            AND customers.user_id = NULLIF(
                current_setting('app.current_user_id', true), ''
            )::bigint
        )
    );

-- Customers can access only their own accounts; tellers and administrators can access all accounts.
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;

CREATE POLICY account_access ON accounts
    FOR ALL
    USING (
        current_setting('app.current_role', true) IN ('admin', 'teller')
        OR (
            current_setting('app.current_role', true) = 'customer'
            AND EXISTS (
                SELECT 1
                FROM customers
                WHERE customers.customer_id = accounts.customer_id
                  AND customers.user_id = NULLIF(
                      current_setting('app.current_user_id', true), ''
                  )::bigint
            )
        )
    );

-- Customers can only access their own transactions; tellers and administrators can access all transactions.
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY transaction_access ON transactions
    FOR ALL
    USING (
        current_setting('app.current_role', true) IN ('admin', 'teller')
        OR (
            current_setting('app.current_role', true) = 'customer'
            AND EXISTS (
                SELECT 1
                FROM accounts
                JOIN customers
                  ON customers.customer_id = accounts.customer_id
                WHERE accounts.account_id = transactions.account_id
                  AND customers.user_id = NULLIF(
                      current_setting('app.current_user_id', true), ''
                  )::bigint
            )
        )
    );
