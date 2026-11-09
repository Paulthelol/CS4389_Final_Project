-- Employees
INSERT INTO employees (username, password_hash, role)
VALUES
    -- Demo password for each employee is the same as their username.
    ('teller1',
     '$argon2id$v=19$m=65536,t=3,p=4$iiDbJvJaQKieOnLOEk9kpg$cp4OLLOgJtEGlM8Ub5NC3guamNQxorJZ1ZD+Vy5kDk4',
     'teller'),
    ('teller2',
     '$argon2id$v=19$m=65536,t=3,p=4$nhbv/+YBFRq76L/IOUTJHg$ZbGvWgN6X1bXxj/rM79BdRT8HyFyzYwCXl5O9Dg3aJ4',
     'teller'),
    ('admin1',
     '$argon2id$v=19$m=65536,t=3,p=4$SzxlRGgpuqaGCWLVNudOiA$SxkW07SHt8ZWBoGWhk91mUxn8NXjpSiKVqsq/9KgXfA',
     'admin');


-- Customers
INSERT INTO customers (first_name, last_name, ssn, email, password_hash)
VALUES
    -- Demo password for each customer is the same as the local part of their email address.
    ('Alice', 'Johnson', '111-22-3333', 'alice@example.com',
     '$argon2id$v=19$m=65536,t=3,p=4$M7rHPMwu5wmWkQvcTCT5SQ$5hDNkHTZfKE7NRlmRbC8KineHosOjyZfSOe96EVp+g0'),
    ('Bob', 'Smith', '444-55-6666', 'bob@example.com',
     '$argon2id$v=19$m=65536,t=3,p=4$gv5ClHnAI2cwGuW5ilNlrg$xMJjTrBvHQi0R2nY29OGYYbdtLYUD6TYXBd4me1/F8E');

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