# Customers API Postman tests

Postman tests for the Customers routes in [`backend/routes/customers.py`](../../backend/routes/customers.py),
run against the **secure** configuration (`DEMO_MODE=false`,
`API_SECURITY_ENABLED=true`, `DB_ACCESS_MODE=appuser`).

| File | Purpose |
| :--- | :--- |
| `CS4389_Customers_API.postman_collection.json` | Postman Collection v2.1, 30 requests in 5 folders |
| `CS4389_Local_Secure.postman_environment.json` | Environment template. Passwords and tokens are empty |
| `sanitize-report.js` | Turns a raw Newman JSON report into token-free evidence |
| `evidence/` | Sanitized results from a real run |
| `SCREENSHOT_CHECKLIST.md` | Steps for capturing report screenshots in VS Code |

## What the collection covers

Run the folders in order. Later requests use IDs and tokens saved by earlier ones.

- **A. Authentication prerequisites.** A1 checks that the server is in secure mode and stops the run if it isn't. A2 logs in as the admin and A3 as Alice, saving their tokens.
- **B. Customers CRUD (admin).** Creates one synthetic customer with a random SSN in the never-issued 900–999 range and a unique `postman.test.*@example.com` email. Then it lists, reads, PATCHes (including `O'Connor`), and PUTs that customer. It also checks validation (400), duplicate email (409), and that rejected creates leave no record behind.
- **C. Registration.** Sets the new customer's password with the one-time setup token, checks that the token can't be reused, and logs in as the new customer.
- **D. Security and negative cases.** Alice can read her own record (200) but not another customer's (404). She gets 403 for listing, creating, and updating. Requests with no token or an invalid token get 401. The vulnerable demo search returns 404.
- **E. Cleanup.** Deletes only the customer created in B1, confirms it's gone, then logs out and clears the runtime secrets.

A collection-level test also runs after **every** request. It fails if any
response contains `password_hash` or an unmasked SSN.

Deletion is limited to `created_customer_id`. B1 clears that value before it
creates a customer, and E1 skips the request if the ID is missing or belongs to
a seeded customer.

## Start the stack (secure mode)

Use a disposable database. The repo's demo databases keep their data in memory:

```sh
docker compose -f .devcontainer/docker-compose.demo-db.yml up -d --wait secure-db
```

Start Flask from the repository root.

PowerShell:

```powershell
$env:DEMO_MODE = 'false'
$env:API_SECURITY_ENABLED = 'true'
$env:DB_HOST = '127.0.0.1'
$env:DB_PORT = '55431'
$env:DB_ACCESS_MODE = 'appuser'
.\.venv\Scripts\python.exe -m flask --env-file .env.example --app backend/app.py:create_app run --host 127.0.0.1 --port 5000
```

macOS/Linux shell:

```sh
DEMO_MODE=false API_SECURITY_ENABLED=true DB_ACCESS_MODE=appuser DB_HOST=127.0.0.1 DB_PORT=55431 \
  python3 -m flask --env-file .env.example --app backend/app.py:create_app run --host 127.0.0.1 --port 5000
```

On macOS, port 5000 is often taken by AirPlay Receiver. If so, use
`--port 5001` and set `base_url` to `http://127.0.0.1:5001`.

Check the mode before testing. The response should be `{"api_security_enabled":true,"demo_mode":false}`:

```sh
curl http://127.0.0.1:5000/auth/demo/status
```

Postman requests go directly to Flask, without the Vite `/api` prefix.

## Run in the Postman VS Code extension

1. Open the Postman view in the VS Code activity bar and sign in if prompted.
2. Choose **Import** and select both JSON files in this folder.
3. Open the **CS4389 Local Secure** environment and select it as the active environment.
4. Set **current values** for `admin_password` and `alice_password`. The seeded demo passwords are documented in [`database/init/02_demo_data.sql`](../../database/init/02_demo_data.sql). Change `base_url` if Flask isn't on port 5000.
5. Run the **CS4389 Customers API** collection with the collection runner, or send the requests one by one in order.

Don't export or share the environment after a run without checking it. E6
clears the tokens, but a run that stops early can leave them in the current
values.

## Run from the command line (Newman)

Newman doesn't need to be a project dependency. `npx` fetches it into its cache:

```sh
npx newman@6 run tests/postman/CS4389_Customers_API.postman_collection.json \
  -e tests/postman/CS4389_Local_Secure.postman_environment.json \
  --env-var base_url=http://127.0.0.1:5000 \
  --env-var admin_password="$ADMIN_PASSWORD" \
  --env-var alice_password="$ALICE_PASSWORD" \
  --reporters cli,json --reporter-json-export /tmp/raw-newman-report.json

node tests/postman/sanitize-report.js /tmp/raw-newman-report.json tests/postman/evidence
```

The raw Newman report contains bearer tokens, the setup token, and response
bodies. Keep it outside the repository and delete it after sanitizing. Only
the output of `sanitize-report.js` belongs in `evidence/`.

To reset the data, run `docker compose -f .devcontainer/docker-compose.demo-db.yml down`.
The demo databases don't keep data between runs.
