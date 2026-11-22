# Customers API test summary

Generated from a Newman run of `CS4389 Customers API`.

- Started: 2026-11-22T23:04:20.040Z
- Completed: 2026-11-22T23:04:21.108Z
- Requests: 30 (PASS 30, FAIL 0, NOT RUN 0)
- Assertions: 121 (0 failed)

| Test | Method | Path | Status | Result |
| :--- | :--- | :--- | ---: | :--- |
| A1 Server is in secure mode | GET | `/auth/demo/status` | 200 | PASS |
| A2 Employee login (admin) | POST | `/auth/employees/login` | 200 | PASS |
| A3 Customer login (Alice) | POST | `/auth/customers/login` | 200 | PASS |
| B1 Create customer | POST | `/customers` | 201 | PASS |
| B2 List customers | GET | `/customers` | 200 | PASS |
| B3 Get created customer | GET | `/customers/3` | 200 | PASS |
| B4 PATCH created customer name (apostrophe) | PATCH | `/customers/3` | 200 | PASS |
| B5 Get created customer after PATCH | GET | `/customers/3` | 200 | PASS |
| B6 PUT created customer (partial) | PUT | `/customers/3` | 200 | PASS |
| B7 Create with missing fields is rejected | POST | `/customers` | 400 | PASS |
| B8 Create with invalid SSN format is rejected | POST | `/customers` | 400 | PASS |
| B9 Invalid creates were not persisted | GET | `/customers` | 200 | PASS |
| B10 Create with duplicate email is rejected | POST | `/customers` | 409 | PASS |
| C1 Register created customer password | POST | `/auth/customers/register` | 201 | PASS |
| C2 Setup token cannot be reused | POST | `/auth/customers/register` | 400 | PASS |
| C3 New customer can log in | POST | `/auth/customers/login` | 200 | PASS |
| D1 Alice reads her own record | GET | `/customers/1` | 200 | PASS |
| D2 Alice cannot read another customer | GET | `/customers/2` | 404 | PASS |
| D3 Alice cannot list all customers | GET | `/customers` | 403 | PASS |
| D4 No Authorization header | GET | `/customers` | 401 | PASS |
| D5 Invalid bearer token | GET | `/customers` | 401 | PASS |
| D6 Alice cannot create a customer | POST | `/customers` | 403 | PASS |
| D7 Alice cannot update her record | PATCH | `/customers/1` | 403 | PASS |
| D8 Vulnerable demo search is disabled | GET | `/customers/vulnerable/search?name=...` | 404 | PASS |
| E1 Delete created customer | DELETE | `/customers/3` | 200 | PASS |
| E2 Deleted customer is gone | GET | `/customers/3` | 404 | PASS |
| E3 Deleted customer's session no longer works | GET | `/customers/3` | 401 | PASS |
| E4 Logout Alice | POST | `/auth/logout` | 200 | PASS |
| E5 Alice token rejected after logout | GET | `/customers/1` | 401 | PASS |
| E6 Logout admin | POST | `/auth/logout` | 200 | PASS |
