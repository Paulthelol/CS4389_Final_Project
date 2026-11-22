# Database security class walkthrough

The two databases start with the same synthetic banking records. Present the
**insecure database comparison first**, then switch to the **secure database**.
The presentation covers row-level security (RLS), SQL injection prevention,
and data masking.

## Presentation walkthrough

1. **Start with the insecure database.** Open Alice's account and statement
   from the employee home. Show one mock deposit so the audience can see
   what a normal statement looks like. In PostgreSQL, show the administrator
   role and the visibility check. “This connection sees both seeded accounts.
   The row policies are present, but PostgreSQL does not apply them to this
   superuser connection.”
2. **Switch to the secure database.** Stop Flask, start it with the secure
   settings, then refresh the browser. Sign in as Alice and open the
   statement for account `1`. Make a mock deposit first if this copy has
   an empty statement. Try account `2` to show **Account not found**.
   “The app checks account ownership. In PostgreSQL, I can also show the
   database enforcing its own policies.” Run the visibility check under
   Alice's customer context and point out the single visible account.
3. **Explain how the app handles text input.** Sign in as staff, edit Alice
   on **Customers**, and save `O'Connor` as her last name. “When input
   becomes part of SQL text, the database can interpret it as part of the
   command. The app sends this name as a bound value, so the apostrophe
   stays part of the name.” Show where Flask binds the name.
   [Customer update code](backend/routes/customers.py#L241)
4. **Finish with masking.** On **Customers**, show Alice's SSN as
   `***-**-3333`. On **Manage accounts and balances**, show account `1` as
   `*****0001`. Compare these with the synthetic values in the seed file.
   “Row policies determine which records a connection can see. Masking
   determines which parts of those records appear on screen.” The website
   uses the masking views in both runs.

## Prepare

1. Follow the [Class Demo Quickstart](README.md#class-demo-quickstart) to start
   both demo databases and Vite on the host. Keep a third PowerShell window
   at the repository root for PostgreSQL checks.
2. Both databases start with Alice's account `1` and Bob's account `2`.
   Fresh copies have an empty transaction history. Make a mock $10 deposit
   on Alice's account in each run to give the statement an entry.

## 1. Insecure database comparison

1. Start Flask on port `5000` with API security disabled and the insecure
   database selected. The database connection uses `postgres` on port `55432`.

   ```powershell
   $env:DEMO_MODE = 'true'
   $env:API_SECURITY_ENABLED = 'false'
   $env:DB_HOST = '127.0.0.1'
   $env:DB_PORT = '55432'
   $env:DB_ACCESS_MODE = 'superuser'
   .\.venv\Scripts\python.exe -m flask --env-file .env.example --app backend/app.py:create_app run --host 127.0.0.1 --port 5000
   ```

2. Open [localhost:5173](http://127.0.0.1:5173). The website detects the
   insecure configuration and opens directly in the employee interface as the
   demo administrator, with no sign-in required.
3. Open **Run database demo searches** and select customers, accounts, or
   employees.

   First enter a normal customer value such as `Alice` and select **Search**.
   This demonstrates the intended exact-name lookup.

   Next enter this payload in the customer search field:

   ```text
   %' OR '1'='1
   ```

   Select **Search** again. The backend places this text directly inside the
   SQL statement, producing the equivalent of:

   ```sql
   WHERE first_name = '%'
   OR '1'='1';
   ```

   The quote and operator text turn the value into SQL syntax. The
   `'1'='1'` condition is always true, so the database can return every
   customer instead of only a customer whose first name is Alice.

   Accounts and employees use the same technique: switch to account or employee
   search and enter the payload. Account search substitutes it into
   `account_number`, while employee search substitutes it into `username`.

   The vulnerable endpoints called by this page are:

   - `/customers/vulnerable/search?name=...`
   - `/accounts/vulnerable/search?name=...`
   - `/employees/vulnerable/search?name=...`

4. Open **Manage accounts and balances**, look at Alice's account `1`, and
   make the mock deposit if needed. Go **Back home**, open
   **View account statements**, and show account `1`'s statement entry.
5. Open PostgreSQL from the third PowerShell window.

   ```powershell
   docker compose -f .devcontainer/docker-compose.demo-db.yml exec insecure-db psql -X
   ```

   At the `psql` prompt, run this read-only check.

   ```sql
   SELECT current_user AS db_role,
          row_security_active('accounts'::regclass) AS accounts_rls,
          row_security_active('transactions'::regclass) AS transactions_rls,
          count(*) AS visible_accounts
   FROM accounts;
   ```

   The expected result on the seed data is `postgres | f | f | 2`.
   Explain that the PostgreSQL superuser bypasses the installed row policies.
   Flask still checks ownership before serving an account through the website.
   Exit `psql` with `\q`.

6. Show Alice's synthetic source values, SSN `111-22-3333` and account number
   `100000001`, in the [seed data](database/init/02_demo_data.sql).
   Label these as source values for the masking comparison.

## 2. Secure database

1. Stop Flask, restart it with API security enabled, and select the secure
   database. The database connection uses `banking_app` on port `55431`.

   ```powershell
   $env:DEMO_MODE = 'false'
   $env:API_SECURITY_ENABLED = 'true'
   $env:DB_HOST = '127.0.0.1'
   $env:DB_PORT = '55431'
   $env:DB_ACCESS_MODE = 'appuser'
   .\.venv\Scripts\python.exe -m flask --env-file .env.example --app backend/app.py:create_app run --host 127.0.0.1 --port 5000
   ```

   Refresh the browser. The normal customer and employee login pages return.
2. Sign in as Alice and open her statement for account `1`. Make
   the mock deposit on this copy if needed. The normal statement still
   loads. Look up seeded account `2` from Alice's statement page to show
   the website returning **Account not found**. This is the app's ownership
   check. Use the next step to demonstrate PostgreSQL's own enforcement.
3. Open PostgreSQL under the restricted role.

   ```powershell
   docker compose -f .devcontainer/docker-compose.demo-db.yml exec secure-db psql -X
   ```

   Apply Alice's customer context for one read-only transaction, then repeat
   the visibility check.

   ```sql
   BEGIN READ ONLY;
   SELECT set_config('app.current_role', 'customer', true),
          set_config('app.current_customer_id', '1', true);

   SELECT current_user AS db_role,
          row_security_active('accounts'::regclass) AS accounts_rls,
          row_security_active('transactions'::regclass) AS transactions_rls,
          count(*) AS visible_accounts
   FROM accounts;
   ROLLBACK;
   ```

   The expected result is `banking_app | t | t | 1`. PostgreSQL applies the
   [row policies](database/init/03_rls.sql) and the same database query now
   sees only Alice's account. Exit with `\q`.
4. Sign out and sign in as `admin1`. Open **Manage customers and setup
   tokens**, edit Alice's last name to `O'Connor`, leave the SSN field blank,
   and choose **Save customer**. Point out that the apostrophe is stored as
   part of the name. Show the
   [customer update](backend/routes/customers.py#L241) or
   [statement lookup](backend/routes/accounts.py#L191) code and explain
   that the application sends the query and bound values separately.
5. On **Customers**, show the live masked SSN `***-**-3333`. On **Manage
   accounts and balances**, show the masked account number `*****0001`.
   Compare them with the synthetic source values from the first run.
   The [PostgreSQL views](database/init/05_masking_views.sql) provide these
   visible values in both runs.

The connection switch demonstrates RLS. Both runs use bound parameters and
masked views. The quotation example illustrates parameter binding in the
working app, and the source-to-screen comparison illustrates masking.
