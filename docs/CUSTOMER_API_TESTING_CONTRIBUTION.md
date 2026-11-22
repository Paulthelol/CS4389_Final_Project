# Customers API testing

## Objective

Check that the Customers API works correctly and enforces its security rules
in the secure configuration. The rules covered are authentication, role
checks, record ownership, SSN masking, and input validation. The tests are a
reproducible Postman collection in [`tests/postman/`](../tests/postman/).

## Environment

| Item | Value |
| :--- | :--- |
| Run date | 2026-11-22, 23:04:20–23:04:21 UTC |
| Backend | Flask (`backend/app.py:create_app`) on `http://127.0.0.1:5001`, started from the macOS host |
| Configuration | `DEMO_MODE=false`, `API_SECURITY_ENABLED=true`, `DB_ACCESS_MODE=appuser` (checked by request A1) |
| Database role | `banking_app`: not a superuser, no `BYPASSRLS` |
| Database | Disposable local PostgreSQL **18.6** cluster on port 55431, built from `database/init/01`–`07` |
| Runner | Newman 6.2.3 (the Postman collection runner CLI) |
| Data | Seeded Alice (ID 1) and Bob (ID 2), plus one synthetic customer that the run created and then deleted |

**Deviations from the usual setup:**

- The repo's Docker demo database (`postgres:17`) couldn't be used because Docker Hub was unreachable from this machine. I ran the same init scripts on a temporary PostgreSQL 18 cluster instead.
- Flask ran on port 5001 because macOS AirPlay Receiver holds port 5000.

## Results

**30 of 30 requests passed, with 121 of 121 assertions** (0 failed, 0 not run).
The machine-generated results are in
[`customers_test_results.json`](../tests/postman/evidence/customers_test_results.json)
and [`customers_test_summary.md`](../tests/postman/evidence/customers_test_summary.md).

| ID | Test | Method | Endpoint | Expected | Actual | Result |
| :- | :--- | :--- | :--- | ---: | ---: | :--- |
| A1 | Server is in secure mode | GET | `/auth/demo/status` | 200 | 200 | PASS |
| A2 | Employee login (admin) | POST | `/auth/employees/login` | 200 | 200 | PASS |
| A3 | Customer login (Alice) | POST | `/auth/customers/login` | 200 | 200 | PASS |
| B1 | Create customer | POST | `/customers` | 201 | 201 | PASS |
| B2 | List customers | GET | `/customers` | 200 | 200 | PASS |
| B3 | Get created customer | GET | `/customers/3` | 200 | 200 | PASS |
| B4 | PATCH created customer name (apostrophe) | PATCH | `/customers/3` | 200 | 200 | PASS |
| B5 | Get created customer after PATCH | GET | `/customers/3` | 200 | 200 | PASS |
| B6 | PUT created customer (partial) | PUT | `/customers/3` | 200 | 200 | PASS |
| B7 | Create with missing fields is rejected | POST | `/customers` | 400 | 400 | PASS |
| B8 | Create with invalid SSN format is rejected | POST | `/customers` | 400 | 400 | PASS |
| B9 | Invalid creates were not persisted | GET | `/customers` | 200 | 200 | PASS |
| B10 | Create with duplicate email is rejected | POST | `/customers` | 409 | 409 | PASS |
| C1 | Register created customer password | POST | `/auth/customers/register` | 201 | 201 | PASS |
| C2 | Setup token cannot be reused | POST | `/auth/customers/register` | 400 | 400 | PASS |
| C3 | New customer can log in | POST | `/auth/customers/login` | 200 | 200 | PASS |
| D1 | Alice reads her own record | GET | `/customers/1` | 200 | 200 | PASS |
| D2 | Alice cannot read another customer | GET | `/customers/2` | 404 | 404 | PASS |
| D3 | Alice cannot list all customers | GET | `/customers` | 403 | 403 | PASS |
| D4 | No Authorization header | GET | `/customers` | 401 | 401 | PASS |
| D5 | Invalid bearer token | GET | `/customers` | 401 | 401 | PASS |
| D6 | Alice cannot create a customer | POST | `/customers` | 403 | 403 | PASS |
| D7 | Alice cannot update her record | PATCH | `/customers/1` | 403 | 403 | PASS |
| D8 | Vulnerable demo search is disabled | GET | `/customers/vulnerable/search?name=...` | 404 | 404 | PASS |
| E1 | Delete created customer | DELETE | `/customers/3` | 200 | 200 | PASS |
| E2 | Deleted customer is gone | GET | `/customers/3` | 404 | 404 | PASS |
| E3 | Deleted customer's session no longer works | GET | `/customers/3` | 401 | 401 | PASS |
| E4 | Logout Alice | POST | `/auth/logout` | 200 | 200 | PASS |
| E5 | Alice token rejected after logout | GET | `/customers/1` | 401 | 401 | PASS |
| E6 | Logout admin | POST | `/auth/logout` | 200 | 200 | PASS |

**Extra checks:**

- **The secure-mode guard works.** I also ran the collection against a separate Flask instance in insecure demo mode (`DEMO_MODE=true`, `API_SECURITY_ENABLED=false`). A1 failed its two mode assertions and the run stopped after that one request, so security results can't be recorded against the wrong configuration.
- **Cleanup was complete.** After the secure run, the database held only the seeded customers 1 and 2.

## What the results show

- **CRUD works for employees.** An admin created a customer (201), listed it, read it, updated it with PATCH and PUT, and deleted it (200). A later read returned 404. B5 re-read the record after the PATCH, which shows the change was saved rather than only echoed back.
- **SSNs are masked.** Every customer object returned had an SSN in the form `***-**-NNNN`. B1 checked that the last four digits matched the SSN that was submitted. A check after every request found no `password_hash` and no unmasked SSN in any of the 30 responses. The masking comes from the `customers_masked` database view, so the raw SSN never leaves PostgreSQL through these routes.
- **Input is validated and treated as data.** Missing fields and a malformed SSN were rejected with 400, and B9 confirmed that neither left a record behind. A duplicate email returned 409. In B4 the name `O'Connor` was stored and read back exactly as typed. Its apostrophe was treated as part of the name, not as SQL, because the backend sends values separately from the query (parameterized SQL).
- **Role-based access works.** Customer Alice got 403 when she tried to list, create, or update customers, including updating her own record. Those actions are for employees only.
- **Record ownership works.** Alice can read her own record (200). Asking for Bob's record returned 404, not 403, so she can't tell whether another customer exists. Two layers enforce this: the route's own ownership check and PostgreSQL row-level security for the `banking_app` role.
- **Setup tokens and sessions behave correctly.** The one-time setup token worked once (201) and was refused the second time (400). Tokens stopped working after logout (E5), and after their customer was deleted (E3), because sessions are deleted along with the customer.

**401, 403, and 404:**

- **401 Unauthorized:** the server doesn't know who you are. The token is missing, invalid, or logged out (D4, D5, E3, E5).
- **403 Forbidden:** the server knows who you are, but your role can't use this action (D3, D6, D7).
- **404 Not Found:** the record doesn't exist for you. It's used for another customer's record (D2) and for the disabled demo endpoint (D8), so neither existence is revealed.

## Screenshots

Screenshots of the Postman VS Code extension haven't been captured yet,
because the extension can't be driven automatically. Take them by following
[`tests/postman/SCREENSHOT_CHECKLIST.md`](../tests/postman/SCREENSHOT_CHECKLIST.md):

1. `evidence/screenshots/01_admin_login.png`: admin login, 200, token redacted *(not yet captured)*
2. `evidence/screenshots/02_create_customer.png`: create customer, 201, masked SSN, setup token redacted *(not yet captured)*
3. `evidence/screenshots/03_get_customer.png`: get customer, 200, masked SSN *(not yet captured)*
4. `evidence/screenshots/04_patch_customer.png`: PATCH, 200, `O'Connor`, masked SSN *(not yet captured)*
5. `evidence/screenshots/05_alice_other_customer_404.png`: Alice reads Bob, 404 *(not yet captured)*
6. `evidence/screenshots/06_alice_list_403.png`: Alice lists customers, 403 *(not yet captured)*

## Contribution summary (for the final report)

I tested the Customers API in the application's secure configuration, with
the backend connecting as the restricted `banking_app` database role. I built
a Postman collection of 30 requests and 121 assertions. It covers the full
create, read, update, and delete cycle for a synthetic customer, customer
registration with the one-time setup token, and the negative cases that show
the access rules hold. Running it with Newman against a disposable database
built from the project's own initialization scripts, every request and
assertion passed. A check after every response confirmed that no password
hash or unmasked SSN was returned.

The results show that the API separates authentication (401), role
permissions (403), and record ownership (404 for another customer's data). A
customer could read only their own record and couldn't list, create, or
update customers. The intentionally vulnerable SQL injection search endpoint
was disabled in secure mode. A name containing an apostrophe was stored
literally, which is consistent with parameterized queries. The collection
checks that the server is in secure mode before running, deletes only the
record it created, and saves only sanitized results without tokens.

## Issues and limitations

**Possible defect (outside the Customers routes): `audit_logs.db_user`
records `postgres` instead of `banking_app`.** During the run, every audit row
for the test customer had `db_user = postgres`, although Flask connected as
`banking_app`. The likely cause is in
[`database/init/06_audit_log.sql`](../database/init/06_audit_log.sql):
`db_user` defaults to `current_user` (line 12), but `fn_audit_log()` is
`SECURITY DEFINER` (line 25). Inside that function, `current_user` is the
function's owner. `session_user` would record the login role instead. I
haven't changed this; it's reported for the database owner to decide.

**Not tested:**

- **A customer deleting their own record.** `DELETE /customers/<id>` lets the record's owner delete it ([`customers.py:301-302`](../backend/routes/customers.py#L301-L302)). Testing that would have meant deleting a seeded customer. Whether customers should be able to delete themselves is worth confirming as a design decision.
- **The teller role.** All employee tests used the admin account.
- **The vulnerable search without a token.** `@employee_required` runs before the `DEMO_MODE` check ([`customers.py:334-337`](../backend/routes/customers.py#L334-L337)), so an unauthenticated request likely gets 401 instead of 404. That would reveal that the route exists. This comes from reading the code and wasn't run.

**Environment limits:** the run used PostgreSQL 18 instead of 17, ran on the
macOS host rather than in the Dev Container, and used Newman rather than the
VS Code extension's runner. The collection file is the same either way.

**Suggested follow-up tests:**

- Repeat the employee tests with `teller1`.
- Test a customer deleting their own record against a disposable customer created for that purpose.
- Test that an expired session (past `SESSION_TTL_HOURS`) gets 401.
- Run the collection in CI against the Docker demo database on every pull request.

## Presentation script (about 40 seconds)

> I tested the Customers API in the secure configuration, where the backend
> uses a restricted database role with row-level security. I wrote a Postman
> collection of 30 requests that creates a test customer, reads it, updates
> it, and deletes it, and all 30 passed. Every customer we got back had a
> masked SSN, and no response ever included a password hash. Then I tried
> to break the access rules. With no token or a bad token, the API returns
> 401. When a customer tries staff-only actions like listing everyone, it
> returns 403. When Alice asks for Bob's record, she gets 404, so she can't
> even tell whether it exists. The vulnerable demo endpoint is switched off.
> The tests clean up after themselves and never save tokens.
