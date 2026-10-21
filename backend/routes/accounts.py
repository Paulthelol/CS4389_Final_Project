from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request
from database import get_connection

accounts_bp = Blueprint(
    "accounts",
    __name__,
    url_prefix="/accounts"
)


def account_to_json(row):
    return {
        "account_id": row[0],
        "customer_id": row[1],
        "account_number": "*****" + row[2][-4:],  # mask all but last 4 digits
        "balance": str(row[3])
    }


# CREATE account
@accounts_bp.route("", methods=["POST"])
def create_account():
    data = request.get_json(silent=True) or {}
    customer_id = data.get("customer_id")
    account_number = data.get("account_number")

    if not customer_id or not account_number:
        return jsonify({"error": "customer_id and account_number are required"}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO accounts (customer_id, account_number)
                VALUES (%s, %s)
                RETURNING account_id, customer_id, account_number, balance;
                """,
                (customer_id, account_number)
            )
            account = cur.fetchone()

    return jsonify(account_to_json(account)), 201


# READ all accounts
@accounts_bp.route("", methods=["GET"])
def get_accounts():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT account_id, customer_id, account_number, balance
                FROM accounts
                ORDER BY account_id;
                """
            )
            accounts = cur.fetchall()

    return jsonify([account_to_json(row) for row in accounts]), 200


# READ one account
@accounts_bp.route("/<int:account_id>", methods=["GET"])
def get_account(account_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT account_id, customer_id, account_number, balance
                FROM accounts
                WHERE account_id = %s;
                """,
                (account_id,)
            )
            account = cur.fetchone()

    if account is None:
        return jsonify({"error": "Account not found"}), 404

    return jsonify(account_to_json(account)), 200


# UPDATE account (only the owner can change; balance changes go through deposit/withdraw)
@accounts_bp.route("/<int:account_id>", methods=["PUT"])
def update_account(account_id):
    data = request.get_json(silent=True) or {}
    customer_id = data.get("customer_id")

    if not customer_id:
        return jsonify({"error": "customer_id is required"}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE accounts
                SET customer_id = %s
                WHERE account_id = %s
                RETURNING account_id, customer_id, account_number, balance;
                """,
                (customer_id, account_id)
            )
            account = cur.fetchone()

    if account is None:
        return jsonify({"error": "Account not found"}), 404

    return jsonify(account_to_json(account)), 200


# DELETE account
@accounts_bp.route("/<int:account_id>", methods=["DELETE"])
def delete_account(account_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM accounts WHERE account_id = %s RETURNING account_id;",
                (account_id,)
            )
            deleted = cur.fetchone()

    if deleted is None:
        return jsonify({"error": "Account not found"}), 404

    return jsonify({"message": "Account deleted"}), 200


def parse_amount(value):
    """Return the amount as a Decimal if it's a positive number with at most 2 decimals, else None."""
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    if not amount.is_finite() or amount <= 0 or amount.as_tuple().exponent < -2:
        return None
    return amount


# DEPOSIT
@accounts_bp.route("/<int:account_id>/deposit", methods=["POST"])
def deposit(account_id):
    data = request.get_json(silent=True) or {}
    amount = parse_amount(data.get("amount"))

    if amount is None:
        return jsonify({"error": "amount must be a positive number"}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE accounts
                SET balance = balance + %s
                WHERE account_id = %s
                RETURNING account_id, customer_id, account_number, balance;
                """,
                (amount, account_id)
            )
            account = cur.fetchone()

    if account is None:
        return jsonify({"error": "Account not found"}), 404

    return jsonify(account_to_json(account)), 200


# WITHDRAW
@accounts_bp.route("/<int:account_id>/withdraw", methods=["POST"])
def withdraw(account_id):
    data = request.get_json(silent=True) or {}
    amount = parse_amount(data.get("amount"))

    if amount is None:
        return jsonify({"error": "amount must be a positive number"}), 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Check and subtract in one query so two withdrawals can't overdraw
            cur.execute(
                """
                UPDATE accounts
                SET balance = balance - %s
                WHERE account_id = %s AND balance >= %s
                RETURNING account_id, customer_id, account_number, balance;
                """,
                (amount, account_id, amount)
            )
            account = cur.fetchone()

            if account is None:
                cur.execute("SELECT 1 FROM accounts WHERE account_id = %s;", (account_id,))
                if cur.fetchone() is None:
                    return jsonify({"error": "Account not found"}), 404
                return jsonify({"error": "Insufficient funds"}), 400

    return jsonify(account_to_json(account)), 200

# TODO: record deposits/withdrawals once the schema team adds a transactions table