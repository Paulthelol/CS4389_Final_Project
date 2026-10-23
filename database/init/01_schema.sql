CREATE TABLE employees (
    employee_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL
        CHECK (role IN ('teller', 'admin'))
);

CREATE TABLE customers (
    customer_id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    ssn VARCHAR(11) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE
);

CREATE TABLE accounts (
    account_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL
        REFERENCES customers(customer_id),
    account_number VARCHAR(20) NOT NULL UNIQUE,
    balance NUMERIC(12, 2) NOT NULL DEFAULT 0.00
);

CREATE TABLE transactions (
    transaction_id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL
        REFERENCES accounts(account_id),
    employee_id BIGINT NOT NULL
        REFERENCES employees(employee_id),
    amount NUMERIC(12, 2) NOT NULL  -- max of 9999999999.99 ($10 billion)
        CHECK (amount <> 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
    session_id BIGSERIAL PRIMARY KEY,
    employee_id BIGINT NOT NULL
        REFERENCES employees(employee_id)
        ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

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
    FOR SELECT
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