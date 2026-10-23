--tellers can only access their own rows in employees table, admin can access all
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;

CREATE POLICY admin_access ON employees
    FOR ALL
    USING (
        current_setting('app.current_role', true) = 'admin'
        OR employee_id = NULLIF(current_setting('app.current_customer_id', true), '')::bigint
    );


--customers can only access their own data in customers table
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

CREATE POLICY customer_access ON customers 
    FOR ALL
    USING (
        current_setting('app.current_role', true) IN ('admin','teller')
        OR customer_id = NULLIF(current_setting('app.current_customer_id', true), '')::bigint
    );

--customers can only access their own accounts
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;

CREATE POLICY account_access ON accounts
    FOR ALL
    USING (
        current_setting('app.current_role', true) IN ('admin','teller')
        OR customer_id = NULLIF(current_setting('app.current_customer_id', true), '')::bigint
    );

--customers can only access their own transactions
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY transaction_access ON transactions
    FOR ALL
    USING (
        current_setting('app.current_role', true) IN ('admin', 'teller')
        OR EXISTS (
            SELECT 1
            FROM accounts
            WHERE accounts.account_id = transactions.account_id
              AND accounts.customer_id = NULLIF(
                  current_setting('app.current_customer_id', true), ''
              )::bigint
        )
    );