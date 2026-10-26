## Tables

#### users
- `user_id`
- `first_name`
- `last_name`
- `username`
- `password_hash`
- `role` — `customer`, `teller`, or `admin`

#### employees
- `employee_id`
- `user_id`
- `hire_date`

#### customers
- `customer_id`
- `user_id`
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
- `user_id` — the authenticated user who performed the transaction
- `amount` — positive for deposits, negative for withdrawals
- `created_at`

#### sessions
- `session_id`
- `user_id`
- `token_hash`
- `expires_at`
- `created_at`

## Relationships

- Customer `1 → 0..*` Account
- Account `1 → 0..*` Transaction
- User `1 → 0..1` Customer
- User `1 → 0..1` Employee
- User `1 → 0..*` Transaction
- User `1 → 0..*` Session

## UML Class Diagram
```mermaid
classDiagram

class User {
    +BIGINT user_id PK
    +VARCHAR first_name
    +VARCHAR last_name
    +VARCHAR username
    +TEXT password_hash
    +VARCHAR role
}

class Employee {
    +BIGINT employee_id PK
    +BIGINT user_id FK
    +DATE hire_date
}

class Customer {
    +BIGINT customer_id PK
    +BIGINT user_id FK
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
    +BIGINT user_id FK
    +NUMERIC amount
    +TIMESTAMPTZ created_at
}

class Session {
    +BIGINT session_id PK
    +BIGINT user_id FK
    +TEXT token_hash
    +TIMESTAMPTZ expires_at
    +TIMESTAMPTZ created_at
}

Customer "1" --> "0..*" Account : owns
Account "1" --> "0..*" Transaction : has
User "1" --> "0..1" Customer : is
User "1" --> "0..1" Employee : is
User "1" --> "0..*" Transaction : performs
User "1" --> "0..*" Session : has
```