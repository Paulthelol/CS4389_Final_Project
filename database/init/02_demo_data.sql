-- Authentication identities
-- Demo password for each user is the same as their username.
INSERT INTO users (first_name, last_name, username, password_hash, role)
VALUES
    ('Taylor', 'Reed', 'teller1',
     '$argon2id$v=19$m=65536,t=3,p=4$iiDbJvJaQKieOnLOEk9kpg$cp4OLLOgJtEGlM8Ub5NC3guamNQxorJZ1ZD+Vy5kDk4',
     'teller'),
    ('Jordan', 'Lee', 'teller2',
     '$argon2id$v=19$m=65536,t=3,p=4$nhbv/+YBFRq76L/IOUTJHg$ZbGvWgN6X1bXxj/rM79BdRT8HyFyzYwCXl5O9Dg3aJ4',
     'teller'),
    ('Morgan', 'Cruz', 'admin1',
     '$argon2id$v=19$m=65536,t=3,p=4$SzxlRGgpuqaGCWLVNudOiA$SxkW07SHt8ZWBoGWhk91mUxn8NXjpSiKVqsq/9KgXfA',
     'admin'),
    ('Alice', 'Johnson', 'alice',
     '$argon2id$v=19$m=65536,t=3,p=4$M7rHPMwu5wmWkQvcTCT5SQ$5hDNkHTZfKE7NRlmRbC8KineHosOjyZfSOe96EVp+g0',
     'customer'),
    ('Bob', 'Smith', 'bob',
     '$argon2id$v=19$m=65536,t=3,p=4$gv5ClHnAI2cwGuW5ilNlrg$xMJjTrBvHQi0R2nY29OGYYbdtLYUD6TYXBd4me1/F8E',
     'customer');

-- Employee profiles
INSERT INTO employees (user_id, hire_date)
VALUES
    ((SELECT user_id FROM users WHERE username = 'teller1'), '2024-01-15'),
    ((SELECT user_id FROM users WHERE username = 'teller2'), '2024-03-01'),
    ((SELECT user_id FROM users WHERE username = 'admin1'), '2023-08-21');

-- Customers
INSERT INTO customers (user_id, ssn, email)
VALUES
    ((SELECT user_id FROM users WHERE username = 'alice'), '111-22-3333', 'alice@example.com'),
    ((SELECT user_id FROM users WHERE username = 'bob'), '444-55-6666', 'bob@example.com');

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