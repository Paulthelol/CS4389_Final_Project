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

## UML Class Diagram
```mermaid
classDiagram

class Employee {
    +BIGINT employee_id PK
    +VARCHAR username
    +TEXT password_hash
    +VARCHAR role
}

class Customer {
    +BIGINT customer_id PK
    +VARCHAR first_name
    +VARCHAR last_name
    +VARCHAR ssn
    +VARCHAR email
}

class Account {
    +BIGINT account_id PK
    +BIGINT customer_id FK
    +VARCHAR account_number
    +NUMERIC balance
}

class Transaction {
    +BIGINT transaction_id PK
    +BIGINT account_id FK
    +BIGINT employee_id FK
    +NUMERIC amount
    +TIMESTAMPTZ created_at
}

class Session {
    +BIGINT session_id PK
    +BIGINT employee_id FK
    +TEXT token_hash
    +TIMESTAMPTZ expires_at
    +TIMESTAMPTZ created_at
}

Customer "1" --> "0..*" Account : owns
Account "1" --> "0..*" Transaction : has
Employee "1" --> "0..*" Transaction : performs
Employee "1" --> "0..*" Session : has
```