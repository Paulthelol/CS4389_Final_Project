-- Employees
INSERT INTO employees (username, password_hash, role)
VALUES
    -- Replace with password hashes once backend decides on hashing method
    ('teller1', 'REPLACE_WITH_HASH', 'teller'),
    ('teller2', 'REPLACE_WITH_HASH', 'teller'),
    ('admin1',  'REPLACE_WITH_HASH', 'admin');


-- Customers
INSERT INTO customers (first_name, last_name, ssn, email)
VALUES
    ('Alice', 'Johnson', '111-22-3333', 'alice@example.com'),
    ('Bob', 'Smith', '444-55-6666', 'bob@example.com');

-- Accounts
INSERT INTO accounts (customer_id, account_number, balance)
VALUES
    (
        (SELECT customer_id FROM customers WHERE email = 'alice@example.com'),
        '100000001',
        1250.00
    ),
    (
        (SELECT customer_id FROM customers WHERE email = 'bob@example.com'),
        '100000002',
        800.00
    );