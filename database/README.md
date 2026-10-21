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

#### transactions
- `transaction_id`
- `account_id`
- `employee_id`
- `amount` — positive for deposits, negative for withdrawals
- `created_at`

#### sessions
- `session_id`
- `employee_id`
- `token_hash`
- `expires_at`
- `created_at`

## Relationships

- Customer `1 → 0..*` Account
- Account `1 → 0..*` Transaction
- Employee `1 → 0..*` Transaction
- Employee `1 → 0..*` Session

## UML Diagram

```mermaid
erDiagram
    EMPLOYEES ||--o{ TRANSACTIONS : performs
    EMPLOYEES ||--o{ SESSIONS : has
    CUSTOMERS ||--o{ ACCOUNTS : owns
    ACCOUNTS ||--o{ TRANSACTIONS : contains

    EMPLOYEES {
        bigint employee_id PK
        varchar username
        text password_hash
        varchar role
    }

    CUSTOMERS {
        bigint customer_id PK
        varchar first_name
        varchar last_name
        varchar ssn
        varchar email
    }

    ACCOUNTS {
        bigint account_id PK
        bigint customer_id FK
        varchar account_number
        numeric balance
    }

    TRANSACTIONS {
        bigint transaction_id PK
        bigint account_id FK
        bigint employee_id FK
        numeric amount
        timestamptz created_at
    }

    SESSIONS {
        bigint session_id PK
        bigint employee_id FK
        text token_hash
        timestamptz expires_at
        timestamptz created_at
    }
```