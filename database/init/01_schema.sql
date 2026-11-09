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