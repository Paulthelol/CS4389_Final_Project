--tellers can only access their own rows in employees table, admin can access all
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;

CREATE POLICY employee_access ON employees
    FOR ALL
    USING (
        current_setting('app.current_role', true) = 'admin'
        OR (
            current_setting('app.current_role', true) = 'teller'
            AND employee_id = NULLIF(
                current_setting('app.current_employee_id', true), ''
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
            AND customer_id = NULLIF(
                current_setting('app.current_customer_id', true), ''
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
            AND customer_id = NULLIF(
                current_setting('app.current_customer_id', true), ''
            )::bigint
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
                WHERE accounts.account_id = transactions.account_id
                  AND accounts.customer_id = NULLIF(
                      current_setting('app.current_customer_id', true), ''
                  )::bigint
            )
        )
    );