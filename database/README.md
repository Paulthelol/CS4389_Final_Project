## Tables

#### employees
- `employee_id`
- `username`
- `password_hash`
- `role` — `teller` or `admin`

#### customers
- `customer_id`
- `first_name`
- `last_name`
- `ssn` — masked
- `email`

#### accounts
- `account_id`
- `customer_id`
- `account_number` — masked
- `balance`

## Relationships
- Customer `1 → 0..*` Account

## UML Diagram
