from contextlib import contextmanager
from decimal import Decimal, InvalidOperation

import psycopg
from flask import Blueprint, current_app, g, jsonify, request

from database.connection import (
    get_authenticated_connection,
    get_pre_auth_connection,
)
from decorators import token_required, employee_required


accounts_bp = Blueprint(
    "accounts",
    __name__,
    url_prefix="/accounts"
)


@contextmanager
def get_account_connection():
    """
    Return a database connection with the appropriate RLS context.

    Employee requests use the authenticated employee's role and ID.
    Customer requests use the authenticated customer's ID.
    When API security is disabled, the decorators simulate an admin,
    so use the admin database context.
    """
    if not current_app.config.get("API_SECURITY_ENABLED", True):
        with get_pre_auth_connection() as conn:
            yield conn
        return

    user = g.current_user

    if user["type"] == "employee":
        with get_authenticated_connection(
            user["role"],
            employee_id=user["id"]
        ) as conn:
            yield conn

    elif user["type"] == "customer":
        with get_authenticated_connection(
            "customer",
            customer_id=user["id"]
        ) as conn:
            yield conn

    else:
        raise RuntimeError("Unsupported authenticated user type")


def account_to_json(row):
    """Convert a masked account database row into the public API representation."""
    return {
        "account_id": row[0],
        "customer_id": row[1],
        "account_number": row[2],
        "balance": str(row[3])
    }


def get_masked_account(cur, account_id):
    """Retrieve an account's public representation through the masked view."""
    cur.execute(
        """
        SELECT account_id, customer_id, account_number, balance
        FROM accounts_masked
        WHERE account_id = %s;
        """,
        (account_id,)
    )

    return cur.fetchone()


# CREATE account
@accounts_bp.route("", methods=["POST"])
@employee_required
def create_account():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    customer_id = data.get("customer_id")
    if not isinstance(customer_id, int) or isinstance(customer_id, bool) or customer_id <= 0:
        return jsonify({"error": "Invalid customer_id"}), 400

    account_number = data.get("account_number")
    if not isinstance(account_number, str) or not account_number.strip():
        return jsonify({"error": "Invalid account_number"}), 400

    account_number = account_number.strip()
    if len(account_number) > 20:
        return jsonify({"error": "Account number is too long"}), 400

    try:
        with get_account_connection() as conn:
            with conn.cursor() as cur:
                # Create the account without returning the raw account number.
                cur.execute(
                    """
                    INSERT INTO accounts (customer_id, account_number)
                    VALUES (%s, %s)
                    RETURNING account_id;
                    """,
                    (customer_id, account_number)
                )

                account_id = cur.fetchone()[0]

                # Retrieve the account through the masked view.
                account = get_masked_account(cur, account_id)

    except psycopg.errors.UniqueViolation:
        return jsonify({
            "error": "An account with that account number already exists"
        }), 409
    except psycopg.errors.ForeignKeyViolation:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify(account_to_json(account)), 201


# READ all accounts
@accounts_bp.route("", methods=["GET"])
@employee_required
def get_accounts():
    with get_account_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT account_id, customer_id, account_number, balance
                FROM accounts_masked
                ORDER BY account_id;
                """
            )

            accounts = cur.fetchall()

    return jsonify([account_to_json(row) for row in accounts]), 200


# READ one account
@accounts_bp.route("/<int:account_id>", methods=["GET"])
@token_required
def get_account(account_id):
    user = g.current_user

    with get_account_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT account_id, customer_id, account_number, balance
                FROM accounts_masked
                WHERE account_id = %s
                    AND (%s = 'employee' OR customer_id = %s);
                """,
                (account_id, user["type"], user["id"])
            )

            account = cur.fetchone()

    if account is None:
        return jsonify({"error": "Account not found"}), 404

    return jsonify(account_to_json(account)), 200
# UPDATE account (employees only; balance changes go through deposit/withdraw)
@accounts_bp.route("/<int:account_id>", methods=["PUT"])
@employee_required
def update_account(account_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    customer_id = data.get("customer_id")
    if not isinstance(customer_id, int) or isinstance(customer_id, bool) or customer_id <= 0:
        return jsonify({"error": "Invalid customer_id"}), 400

    try:
        with get_account_connection() as conn:
            with conn.cursor() as cur:
                # Update the underlying table without returning the raw account number.
                cur.execute(
                    """
                    UPDATE accounts
                    SET customer_id = %s
                    WHERE account_id = %s
                    RETURNING account_id;
                    """,
                    (customer_id, account_id)
                )

                updated = cur.fetchone()

                if updated is not None:
                    # Retrieve the updated account through the masked view.
                    account = get_masked_account(cur, updated[0])
                else:
                    account = None

    except psycopg.errors.ForeignKeyViolation:
        return jsonify({"error": "Customer not found"}), 404

    if account is None:
        return jsonify({"error": "Account not found"}), 404

    return jsonify(account_to_json(account)), 200
# DELETE account
@accounts_bp.route("/<int:account_id>", methods=["DELETE"])
@employee_required
def delete_account(account_id):
    try:
        with get_account_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM accounts
                    WHERE account_id = %s
                    RETURNING account_id;
                    """,
                    (account_id,)
                )

                deleted = cur.fetchone()

    except psycopg.errors.ForeignKeyViolation:
        return jsonify({
            "error": "Cannot delete an account with existing transactions"
        }), 409

    if deleted is None:
        return jsonify({"error": "Account not found"}), 404

    return jsonify({"message": "Account deleted"}), 200


def parse_amount(value):
    """Return the amount as a Decimal if it's a positive number with at most 2 decimals, else None."""
    if isinstance(value, bool) or value is None:
        return None

    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None

    if (
        not amount.is_finite()
        or amount <= 0
        or amount > Decimal("9999999999.99")
        or amount.as_tuple().exponent < -2
    ):
        return None

    return amount


# DEPOSIT
@accounts_bp.route("/<int:account_id>/deposit", methods=["POST"])
@token_required
def deposit(account_id):
    user = g.current_user

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    amount = parse_amount(data.get("amount"))
    if amount is None:
        return jsonify({"error": "amount must be a positive number"}), 400

    # Employee requests are authorized for all accounts.
    # Customer requests are restricted by their customer ID and RLS.
    customer_id = user["id"] if user["type"] == "customer" else None

    with get_account_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE accounts
                SET balance = balance + %s
                WHERE account_id = %s
                    AND (%s = 'employee' OR customer_id = %s)
                    AND balance <= 9999999999.99 - %s
                RETURNING account_id;
                """,
                (amount, account_id, user["type"], customer_id, amount)
            )

            updated = cur.fetchone()

            if updated is None:
                # Check whether the account exists and is accessible.
                cur.execute(
                    """
                    SELECT 1
                    FROM accounts_masked
                    WHERE account_id = %s
                        AND (%s = 'employee' OR customer_id = %s);
                    """,
                    (account_id, user["type"], customer_id)
                )

                if cur.fetchone() is None:
                    return jsonify({"error": "Account not found"}), 404

                return jsonify({
                    "error": "Deposit would exceed the maximum account balance"
                }), 400

            cur.execute(
                """
                INSERT INTO transactions (account_id, customer_id, employee_id, amount)
                VALUES (%s, %s, %s, %s);
                """,
                (
                    updated[0],
                    user["id"] if user["type"] == "customer" else None,
                    user["id"] if user["type"] == "employee" else None,
                    amount,
                ),
            )

            account = get_masked_account(cur, updated[0])

    return jsonify(account_to_json(account)), 200
# WITHDRAW
@accounts_bp.route("/<int:account_id>/withdraw", methods=["POST"])
@token_required
def withdraw(account_id):
    user = g.current_user

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    amount = parse_amount(data.get("amount"))
    if amount is None:
        return jsonify({"error": "amount must be a positive number"}), 400

    # Employee requests are authorized for all accounts.
    # Customer requests are restricted by their customer ID and RLS.
    customer_id = user["id"] if user["type"] == "customer" else None

    with get_account_connection() as conn:
        with conn.cursor() as cur:
            # Check and subtract in one query so two withdrawals can't overdraw.
            cur.execute(
                """
                UPDATE accounts
                SET balance = balance - %s
                WHERE account_id = %s
                    AND (%s = 'employee' OR customer_id = %s)
                    AND balance >= %s
                RETURNING account_id;
                """,
                (amount, account_id, user["type"], customer_id, amount)
            )

            updated = cur.fetchone()

            if updated is None:
                # Check whether the account exists and is accessible.
                cur.execute(
                    """
                    SELECT 1
                    FROM accounts_masked
                    WHERE account_id = %s
                        AND (%s = 'employee' OR customer_id = %s);
                    """,
                    (account_id, user["type"], customer_id)
                )

                if cur.fetchone() is None:
                    return jsonify({"error": "Account not found"}), 404

                return jsonify({"error": "Insufficient funds"}), 400

            cur.execute(
                """
                INSERT INTO transactions (account_id, customer_id, employee_id, amount)
                VALUES (%s, %s, %s, %s);
                """,
                (
                    updated[0],
                    user["id"] if user["type"] == "customer" else None,
                    user["id"] if user["type"] == "employee" else None,
                    -amount,
                ),
            )

            account = get_masked_account(cur, updated[0])

    return jsonify(account_to_json(account)), 200


